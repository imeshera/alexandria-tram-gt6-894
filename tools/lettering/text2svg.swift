// text2svg: lay out text with CoreText (proper Arabic shaping + bidi) and write glyph outlines as SVG.
// Usage: swift text2svg.swift <out.svg> <font PostScript or family name> <cap/em height mm> <flip 0|1> <text>
// The SVG is in millimetres (viewBox units = mm), y down, origin at the text's top-left.
// flip=1 mirrors horizontally (for lettering read from the opposite side of a sketch plane).
import Foundation
import CoreText
import CoreGraphics

let a = CommandLine.arguments
guard a.count >= 6 else {
    FileHandle.standardError.write("usage: text2svg out.svg font sizeMM flip text\n".data(using: .utf8)!); exit(1)
}
let out = a[1], fontName = a[2], sizeMM = Double(a[3])!, flip = a[4] == "1", text = a[5]

let font = CTFontCreateWithName(fontName as CFString, CGFloat(sizeMM), nil)
let attr = NSAttributedString(string: text, attributes: [kCTFontAttributeName as NSAttributedString.Key: font])
let line = CTLineCreateWithAttributedString(attr)
var ascent: CGFloat = 0, descent: CGFloat = 0, leading: CGFloat = 0
let width = CGFloat(CTLineGetTypographicBounds(line, &ascent, &descent, &leading))
let height = ascent + descent

let path = CGMutablePath()
let runs = CTLineGetGlyphRuns(line) as! [CTRun]
for run in runs {
    let attrs = CTRunGetAttributes(run) as NSDictionary
    let runFont = attrs[kCTFontAttributeName as String] as! CTFont
    let n = CTRunGetGlyphCount(run)
    var glyphs = [CGGlyph](repeating: 0, count: n)
    var pos = [CGPoint](repeating: .zero, count: n)
    CTRunGetGlyphs(run, CFRange(location: 0, length: n), &glyphs)
    CTRunGetPositions(run, CFRange(location: 0, length: n), &pos)
    for i in 0..<n {
        guard let gp = CTFontCreatePathForGlyph(runFont, glyphs[i], nil) else { continue }
        // glyph space: y up, baseline at 0 -> SVG: y down, top at 0
        var t = CGAffineTransform(a: 1, b: 0, c: 0, d: -1, tx: pos[i].x, ty: ascent - pos[i].y)
        if flip { t = t.concatenating(CGAffineTransform(a: -1, b: 0, c: 0, d: 1, tx: width, ty: 0)) }
        path.addPath(gp, transform: t)
    }
}

// Joined Arabic glyphs overlap; merge them so the outline has no self-overlaps and the
// only interior contours are real holes (letter counters). Fusion profiles then map 1:1.
let merged = path.normalized(using: .winding)

var d = ""
func f(_ v: CGFloat) -> String { String(format: "%.3f", Double(v)) }
merged.applyWithBlock { e in
    let p = e.pointee.points
    switch e.pointee.type {
    case .moveToPoint: d += "M\(f(p[0].x)) \(f(p[0].y)) "
    case .addLineToPoint: d += "L\(f(p[0].x)) \(f(p[0].y)) "
    case .addQuadCurveToPoint: d += "Q\(f(p[0].x)) \(f(p[0].y)) \(f(p[1].x)) \(f(p[1].y)) "
    case .addCurveToPoint: d += "C\(f(p[0].x)) \(f(p[0].y)) \(f(p[1].x)) \(f(p[1].y)) \(f(p[2].x)) \(f(p[2].y)) "
    case .closeSubpath: d += "Z "
    @unknown default: break
    }
}
let svg = """
<svg xmlns="http://www.w3.org/2000/svg" width="\(f(width))mm" height="\(f(height))mm" viewBox="0 0 \(f(width)) \(f(height))">
<path fill="black" fill-rule="nonzero" d="\(d)"/>
</svg>
"""
try! svg.write(toFile: out, atomically: true, encoding: .utf8)
print("\(out) \(f(width)) x \(f(height)) mm")
