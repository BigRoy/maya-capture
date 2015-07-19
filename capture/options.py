import sys


class Options(object):
    """The base options class defining the base interface for all options."""
    def set(self, *args, **kwargs):
        pass

    def current(self, *args, **kwargs):
        pass


class ViewportOptions(Options):
    """Viewport options for :func:`capture`"""

    useDefaultMaterial = False
    wireframeOnShaded = False
    displayAppearance = 'smoothShaded'

    # Visibility flags
    nurbsCurves = False
    nurbsSurfaces = False
    polymeshes = True
    subdivSurfaces = False
    cameras = False
    lights = False
    grid = False
    joints = False
    ikHandles = False
    deformers = False
    dynamics = False
    fluids = False
    hairSystems = False
    follicles = False
    nCloths = False
    nParticles = False
    nRigids = False
    dynamicConstraints = False
    locators = False
    manipulators = False
    dimensions = False
    handles = False
    pivots = False
    textures = False
    strokes = False

    def set(self, panel):
        """Applies the options for the panel and camera."""
        from maya import cmds

        options = _parse_options(self)
        # reset the panel first
        cmds.modelEditor(panel,
                         edit=True,
                         allObjects=False,
                         grid=False,
                         manipulators=False)
        cmds.modelEditor(panel, edit=True, **options)

    @staticmethod
    def current(panel):
        """Return the options for the currently defined user-settings"""
        from maya import cmds

        viewport_options = ViewportOptions()
        options = _parse_options(viewport_options)

        # Reset the panel
        cmds.modelEditor(panel,
                         edit=True,
                         allObjects=False,
                         grid=False,
                         manipulators=False)

        for key in options:
            kwargs = {key: True}
            value = cmds.modelEditor(panel, query=True, **kwargs)
            setattr(viewport_options, key, value)

        return viewport_options


class CameraOptions(Options):
    """Camera settings for :func:`capture`

    Camera options are applied to the specified camera and
    then reverted once the capture is complete.

    """

    displayGateMask = False
    displayResolution = False
    displayFilmGate = False

    @staticmethod
    def current(camera):
        """Return the current options of given camera."""
        from maya import cmds

        camera_options = CameraOptions()
        options = _parse_options(camera_options)

        for opt in options:
            try:
                value = cmds.getAttr(camera + "." + opt)
                setattr(camera_options, opt, value)
            except RuntimeError:
                sys.stderr.write("Could not get camera attribute "
                                 "for capture: %s" % opt)
                delattr(camera_options, opt)

        return camera_options

    def set(self, camera):
        """Set the options to the given camera."""
        from maya import cmds

        options = _parse_options(self)

        for opt, value in options.iteritems():
            cmds.setAttr(camera + "." + opt, value)


class DisplayOptions(Options):
    """Display options for :func:`capture`

    Use this struct for background color, anti-alias and other
    display-related options.

    """
    displayGradient = True
    background = (0.631, 0.631, 0.631)
    backgroundTop = (0.535, 0.617, 0.702)
    backgroundBottom = (0.052, 0.052, 0.052)

    _colors = ['background', 'backgroundTop', 'backgroundBottom']
    _prefs = ['displayGradient']

    @staticmethod
    def current():
        """Return the currently set options."""
        from maya import cmds

        options = DisplayOptions()

        for clr in options._colors:
            value = cmds.displayRGBColor(clr, query=True)
            setattr(options, clr, value)

        for pref in options._prefs:
            value = cmds.displayPref(query=True, **{pref: True})
            setattr(options, pref, value)

    def set(self):
        """Applies the options."""
        from maya import cmds

        for clr in self._colors:
            value = getattr(self, clr)
            cmds.displayRGBColor(clr, *value)
        for pref in self._prefs:
            value = getattr(self, pref)
            cmds.displayPref(**{pref: value})


def _parse_options(options):
    """Return dictionary of properties from option-objects"""
    opts = dict()
    for attr in dir(options):
        if attr.startswith("__"):
            continue
        opts[attr] = getattr(options, attr)
    return opts