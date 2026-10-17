# One-off: creates the Fusion design "Alexandria Heritage Tram 894" (Hybrid intent) in the model folder
# "Alexandria Tram Model 3 - Duewag GT6 894" of project Eshera-Personal (looked up by name in the active hub).
import os
import adsk.core, adsk.fusion
ROOT = os.path.dirname(os.path.abspath(__file__))

def run(_context: str):
    g = {'__file__': os.path.join(ROOT, 'common.py')}; exec(open(g['__file__']).read(), g)
    DOC = g['DOC']; app = adsk.core.Application.get()
    if [d for d in app.documents if d.name == DOC or d.name.startswith(DOC + ' v')]:
        print('already open'); return
    folder = g['model_folder'](app)
    for i in range(folder.dataFiles.count):
        if folder.dataFiles.item(i).name == DOC:
            print('exists in the model folder; open it instead'); return
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    des = adsk.fusion.Design.cast(app.activeProduct)
    des.designIntent = adsk.fusion.DesignIntentTypes.HybridDesignIntentType
    doc.saveAs(DOC, folder, 'Ex-Copenhagen Duewag GT6 894 in Alexandria', '')
    print('created', doc.name)
