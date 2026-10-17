# Activates the heritage document and sets a camera. _context: 'iso' | 'left' | 'right' | 'front' | 'rear' | 'top' | 'fit'
# | 'interior' (standing at the rear of section B looking toward the cab; no fit)
import adsk.core, adsk.fusion
DOC = 'Alexandria Heritage Tram 894'
def run(_context: str):
    app = adsk.core.Application.get()
    d = [x for x in app.documents if x.name.startswith(DOC)][0]; d.activate()
    vp = app.activeViewport; cam = vp.camera
    P = adsk.core.Point3D.create
    mode = (_context or 'iso').strip()
    tgt = P(955, 160, 0)
    eyes = {'iso': P(-900, 900, -1700), 'isoL': P(-900, 900, 1700), 'left': P(955, 160, 5000), 'right': P(955, 160, -5000),
            'front': P(-5000, 160, 0), 'rear': P(7000, 160, 0), 'top': P(955, 5000, 1), 'isoR': P(2800, 700, -1600)}
    if mode == 'interior':
        cam.isFitView = False
        cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
        cam.eye = P(1840, 245, 30); cam.target = P(200, 190, -10); cam.upVector = adsk.core.Vector3D.create(0, 1, 0)
        cam.perspectiveAngle = 1.2
        vp.camera = cam
        print('view', mode)
        return
    if mode in eyes:
        cam.isFitView = False
        cam.target = tgt; cam.eye = eyes[mode]; cam.upVector = adsk.core.Vector3D.create(0, 1, 0)
        cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType if mode.startswith('iso') else adsk.core.CameraTypes.OrthographicCameraType
        cam.perspectiveAngle = 0.4      # reset: the interior preset widens it
        vp.camera = cam
    vp.fit()
    print('view', mode)
