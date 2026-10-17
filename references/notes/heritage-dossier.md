# Düwag GT6 894: identification, choice and dimension sheet

*Compiled 2026-10-17. Raw research with every source URL: `research-raw.md` (same folder). Reference photo list:
`../SOURCES.md` and `../manifests/*.csv`. Photogrammetry: `photogrammetry/rect1d.py`, `photogrammetry/grid.py`,
`photogrammetry/underlay_818.py`.*

## The four reference trams

The project started from four photographs of Alexandria trams. Each was identified by type before choosing what
to model; each type is now its own model repository.

| Reference photo | What it is | Model |
|---|---|---|
| 1. Ochre-and-cream **894** | **Düwag GT6** six-axle articulated car, ex-Copenhagen **KS 894**, in Alexandria since 1972 with its number unchanged. Still in service in 2024 on city route 4, then in green and white | [alexandria-tram-gt6-894](https://github.com/imeshera/alexandria-tram-gt6-894) |
| 2. Red-and-cream **601** | The **Raml heritage car**: a four-axle wooden motor car (Oerlikon 1925 or Belgian 1931; sources disagree). **Light blue and cream until about 2019**, red and cream after the restoration (heritage service from 6 Oct 2020) | [alexandria-tram-heritage-601](https://github.com/imeshera/alexandria-tram-heritage-601) |
| 3. Yellow two-car set with a blue stripe | City two-car set, identified as **Ganz-MÁVAG 1201–1230 (1985/86)** (the lookalike Kinki Sharyo 117–130 of 1982 was ruled out on livery and readable fleet numbers). One cab per car, trolley poles | [alexandria-tram-city-1211-1212](https://github.com/imeshera/alexandria-tram-city-1211-1212) |
| 4. Green-and-white **856** | **Another ex-Copenhagen Düwag GT6** (KS 856, delivered 1963, Alexandria 1971), seen from its **rear end**. The "curved two-pane windscreen with open door" is the GT6's rear window and rear-corner door; the side digits that read like "١٠٧" are ٨٥٦ in Naskh | Same type as 894 |

Confidence key used throughout the notes:
- **S**: stated by a source.
- **S?**: sourced, but generic, analog or conflicting.
- **V**: measured from dated photos (photogrammetry).
- **E**: engineering estimate.

## Why the GT6 894

- The brief was "the older style tram that usually runs as a single car, light yellow or light blue, very old style".
  The GT6s are the old cars that run alone, uncoupled, unlike the 2- and 3-car sets. The articulated body is the
  only mismatch with "single car": a GT6 is one vehicle and runs alone; it just bends in the middle.
- **They wore the colours named.** City GT6s were yellow (with cream and a blue waist stripe in c. 2000–2015). A
  refurbished batch wore light blue and white on Raml lines 5/6 in 2019.
- **Two of the four reference photos are GT6s** (894 and 856).
- **It is the most numerous old type:** 99 cars, 1969–2020s.
- **It has the best data:** a sourced length and width; a near-orthogonal broadside photo of the same type (KS 818,
  1969); many dated photos of 894 and its sisters; preserved sisters with interior photos.

**Modelled car:** GT6 **894**, Fusion design **"Alexandria Heritage Tram 894"**. The livery is switchable through
the `livery` user parameter:

| Value | Scheme | Matches |
|---|---|---|
| 1 (default) | Alexandria city: all-over ochre-yellow with a dark-blue waist stripe, pale roof and apron, blue numerals, c. 2000–2015 | "light yellow" |
| 2 | 1974 APTA ochre / cream | Reference photo 1 |
| 3 | Green / white, 2016+ | Reference photo 4 and 894's 2024 colours |
| 4 | Raml light blue / white, 2019 | "light blue" |
| 5 | KS Copenhagen | — |

`panto_on = 1` swaps the trolley pole for the diamond pantograph seen on the 2019 light-blue Raml-line car (899).

---

## 1. Type summary: Düwag GT6, ex-Københavns Sporveje 801–900

| Item | Value | Conf. |
|---|---|---|
| Builder | Düwag, Düsseldorf; Kiepe electrics. 31 of the 100 were delivered as bodyshells and finished in Copenhagen | S |
| Built | 1960–68, seven batches. KS 856: 19 Aug 1963. KS 894: 1966 batch | S |
| Alexandria | 99 cars (841 was lost in Denmark), shipped 1969 / 1971 / 1972. **894 arrived in 1972.** Numbers kept | S |
| Lines | City (El-Madina) network, e.g. routes 1–11; a refurbished batch on Raml lines 5/6 in 2019 | S |
| Type | Six-axle, two-section, **single-ended**, B'2'B'. Doors on the **right side only**; both Denmark and Egypt drive on the right | S |
| Gauge / supply | 1435 mm / 600 V DC | S |
| Collection | **Trolley pole** with a wheel head. In 2019 the Raml-line light-blue car 899 carried a **diamond pantograph** (V, UTM photo) | S / V |
| Seats | 36 seated + 119 standing (KS) | S |
| Liveries | KS yellow/cream (1960–72) → same paint in Alexandria, faded to ochre (1970s–80s) → all-over ochre-yellow (window band included) with a dark-blue waist stripe, a front "V", a pale roof and apron, and blue numerals (c. 2000–2015; 895 and 856 in 2007) → green/white (2016+) → red/white or light-blue/white refurbished batch on the Raml (2019) | S + V |
| Status | Most still listed in service in 2024–26. 894 was green and white on route 4 in Apr 2024; 856 was green and white at Karmouz in Mar 2025. KS 815 and 890 are preserved at Skjoldenæsholm (DK), back since 2001 | S |

### Car 856 (reference photo 4)

Same type. The photo shows the B-section rear (rear window and rear-corner door). There is no separate build.

---

## 2. Dimension sheet (GT6 894)

**Method:** 1-D projective rectification along the car side (`photogrammetry/rect1d.py`). Pixels were picked on the grid overlays and scaled by the sourced 19.095 m body length; the vanishing point comes from window-height and skirt-line convergence.
- **Main source:** KS 818, Sundby depot, 1969 (Commons 41468165). It is a long-lens, near-orthogonal left broadside.
- **Cross-checks:**
  - Alexandria 877 (1977), which is obliquer. Its height and length scales agree with each other if the roof is about 3.1–3.35 m.
  - Fronts: 829, 830 (1977), KS 890 (2025), and rears 801/900 (1960s).
  - The door side: 821 (1974) and the 807/845 door close-ups.

| Parameter | Value | Conf. | Source / note |
|---|---|---|---|
| Length over body | 19,095 mm | S | de.wiki (Straßenbahn Magazin 9/2008); TramTravels 19.10 m |
| Width | 2,200 mm | S | de.wiki, TramTravels (not the 2.35 m Düsseldorf type) |
| Roof crown | 3,150 mm (±100) | V + S? | 818: 3.12–3.15 m. A 1969 Düwag artic is listed at 3.19 m. The cs.wiki generic 3.35 m is for the 2.35 m cars |
| Eave / gutter | 2,650 mm | V | 818 |
| Window band | 1,540–2,490 mm | V | 818 (1.51–2.46 with the rail at y = 615) |
| Waist (top of lower colour) | 1,420 mm | V | 818 |
| Skirt colour line / skirt bottom | 680 / 340 mm | V | 818 |
| Floor | 880 mm | S? | Generic GT6 |
| A section (front → inner end) | 9,590 mm | V | 818 |
| Articulation gap | 600 mm; centre 9,890 mm | V | 818 (Jacobs bogie frame centred at 9.91) |
| Bogie pivots | 3,730 / 9,890 / 15,950 mm (spacing 6.16 / 6.06) | V | 818 bogie frames 2.41–5.09, 8.56–11.26, 14.72–17.22. The GT6-D analog is 6.0 m (S?) |
| Bogie wheelbase / wheel | 1,800 / 680 mm | S? | VBK GT6-D analog |
| Left windows | Cab 0.49–1.81; A: 5 × 1.33 m at a 1.42 pitch from 2.10; B: 5 × 1.30 at a 1.39 pitch from 10.73; rear 17.86–18.97 | V | 818 |
| Right side | Door 1 directly behind the cab corner (0.62–1.92); narrow window; 3 windows; door 2 (7.58–8.88); narrow window ‖ narrow window; door 3 (11.10–12.40); 3 windows; rear-corner door 4 (17.65–18.75) | V (LOW) | 821 (oblique, 3-point fit) + 807/845/890 |
| Doors | 4-panel folding, about 1.30 m; the front door also has lower glazing (KS feature, pl.wiki) | V / S | — |
| Windscreen | 1.50–2.43 m high, 1.64 m chord, two panes | V (MED-LOW) | 829/830/890 ratios |
| Destination glass / route box | 2.60–2.80 m, 1.0 m wide / roof box 0.38 m wide | V | 890, 830 |
| Headlight | Centre 0.79 m, ring Ø 0.30 m | V | 829/830 ratios |
| End taper | About 190 mm per side; end faces about 1.82 m wide | V (LOW) | Rear photo of 801/900 |
| Pole base | x = 5.67 m; pole about 5.2 m long | V / E | 818 |
| Seats | 36: 2+1 layout (doubles on the left, singles on the right), all facing the cab | S (count) / S? (layout, generic GT6) | — |

**Not resolvable from photos:**
- the exact door widths;
- the plan taper shape;
- the tumblehome (E: 45 mm);
- the seat material. The Alexandria 2010 interior photo shows hard brown seat backs; the model uses varnished wood slats (E).

**Biggest uncertainties:**
- **Right-side window and door spacing:** LOW, from the oblique 821 photo.
- **Roof height:** ±0.1 m.
- **Whether 894 had door 2 plated over:** `door2_on`. UTM says "the second door has been eliminated in Alexandria" but gives no date.

---

## 3. Sources (short; full list in research-raw.md)

- de.wikipedia, *Duewag-Gelenkwagen*.
- TramTravels / sporvognsrejser.dk vehicle pages for KS 815, 856 and 890.
- pl/cs/bg.wikipedia, *Duewag GT6* (generic data).
- VBK GT6-D (bogie analog).
- Urban Transport Magazine: "Tram modernisation in Alexandria" (2019) and "Heritage tram service on the Ramleh line" (2020).
- Ahram Gate (2016), on the green livery.
- bus-planet.com fleet notes.
- Transphoto fleet lists.
- Wikimedia Commons: Kurt Rasmussen 1974/77 scans (Attribution), Leif Jørgensen (KS 890, CC BY-SA 4.0), Commons 41468165 (KS 818 broadside).

## Related models

The Alexandria vehicle models are published as separate repositories, each self-contained:

| Repository | Vehicle |
|---|---|
| [alexandria-tram-raml-221-223](https://github.com/imeshera/alexandria-tram-raml-221-223) | Kinki Sharyo Raml three-car set 221–223 |
| [alexandria-tram-raml-dd-224](https://github.com/imeshera/alexandria-tram-raml-dd-224) | Raml double-deck car 224 and its set |
| [alexandria-tram-gt6-894](https://github.com/imeshera/alexandria-tram-gt6-894) | Ex-Copenhagen Düwag GT6 894 (city network) |
| [alexandria-tram-heritage-601](https://github.com/imeshera/alexandria-tram-heritage-601) | Raml heritage car 601 (four-axle wooden motor car) |
| [alexandria-tram-city-1211-1212](https://github.com/imeshera/alexandria-tram-city-1211-1212) | Ganz-MÁVAG city two-car set 1211+1212 |
| [alexandria-lada-taxi](https://github.com/imeshera/alexandria-lada-taxi) | Alexandria Lada taxi |
