package com.ios.motion;

/**
 * Centralized motion configuration containing physics parameters,
 * spring constants, timing parameters, and geometric thresholds.
 *
 * Parameters are documented with physical units and empirical origins.
 */
public final class MotionConfig {

    private MotionConfig() {}

    // =========================================================================
    // 1. SPRING PRESETS (Response in seconds, Damping Ratio dimensionless)
    // =========================================================================

    /** App Launch: Smooth expansion without bounce (zeta=0.86, response=0.50s) */
    public static final double APP_LAUNCH_RESPONSE = 0.50;
    public static final double APP_LAUNCH_DAMPING_RATIO = 0.86;

    /** App Exit / Home Gesture: Snappy return with minimal overshoot (zeta=0.82, response=0.45s) */
    public static final double APP_EXIT_RESPONSE = 0.45;
    public static final double APP_EXIT_DAMPING_RATIO = 0.82;

    /** Workspace Paging: Crisp snapping between home screen pages (zeta=0.88, response=0.38s) */
    public static final double WORKSPACE_PAGE_RESPONSE = 0.38;
    public static final double WORKSPACE_PAGE_DAMPING_RATIO = 0.88;

    /** Spotlight Search: Graceful pull-down with gentle settling (zeta=0.85, response=0.40s) */
    public static final double SPOTLIGHT_RESPONSE = 0.40;
    public static final double SPOTLIGHT_DAMPING_RATIO = 0.85;

    /** Recents / Switcher Card Snap: Controlled settling into card center (zeta=0.84, response=0.42s) */
    public static final double RECENTS_SNAP_RESPONSE = 0.42;
    public static final double RECENTS_SNAP_DAMPING_RATIO = 0.84;

    /** Folder Expansion / Collapse: Tactile card pop (zeta=0.82, response=0.42s) */
    public static final double FOLDER_TRANSITION_RESPONSE = 0.42;
    public static final double FOLDER_TRANSITION_DAMPING_RATIO = 0.82;

    /** Control Center & Notification Panel: Fluid slide-down (zeta=0.84, response=0.44s) */
    public static final double SYSTEMUI_PANEL_RESPONSE = 0.44;
    public static final double SYSTEMUI_PANEL_DAMPING_RATIO = 0.84;

    /** Slider Limits (Volume/Brightness): Snappy rubber-band return (zeta=0.75, response=0.28s) */
    public static final double SLIDER_BOUNCE_RESPONSE = 0.28;
    public static final double SLIDER_BOUNCE_DAMPING_RATIO = 0.75;

    // =========================================================================
    // 2. GESTURE & VELOCITY THRESHOLDS (Pixels / Second & Fractions)
    // =========================================================================

    /** Minimum fling velocity (px/s) to trigger state commit regardless of position */
    public static final double FLING_COMMIT_VELOCITY_PX_S = 450.0;

    /** Fling velocity to cancel / reverse a gesture (px/s) */
    public static final double FLING_CANCEL_VELOCITY_PX_S = -450.0;

    /** Maximum allowed velocity injection to prevent visual explosion */
    public static final double MAX_INJECTED_VELOCITY_PX_S = 3500.0;

    /** Vertical bias ratio for Spotlight gesture disambiguation (|dY| > 1.5 * |dX|) */
    public static final float SPOTLIGHT_VERTICAL_BIAS = 1.5f;

    /** Touch slop compensation threshold in dp */
    public static final float TOUCH_SLOP_DP = 8.0f;

    // =========================================================================
    // 3. GEOMETRY & CORNER RADII (DP units)
    // =========================================================================

    /** Standard iOS app icon corner radius (approx 22.5% of icon size) */
    public static final float ICON_CORNER_RADIUS_DP = 14.0f;

    /** Screen corner radius matching Realme 3 display bezels */
    public static final float SCREEN_CORNER_RADIUS_DP = 24.0f;

    /** App Switcher / Recents card corner radius */
    public static final float RECENTS_CARD_CORNER_RADIUS_DP = 20.0f;

    /** Control Center module corner radius */
    public static final float CC_MODULE_CORNER_RADIUS_DP = 18.0f;

    // =========================================================================
    // 4. JIGGLE (EDIT MODE) PARAMETERS
    // =========================================================================

    /** Jiggle oscillation frequency in Hertz */
    public static final double JIGGLE_FREQUENCY_HZ = 9.5;

    /** Jiggle angular amplitude in degrees */
    public static final float JIGGLE_ANGLE_DEG = 2.2f;

    /** Jiggle translational amplitude in dp */
    public static final float JIGGLE_TRANSLATION_DP = 1.0f;

    /** Scale factor of icons during jiggle edit mode */
    public static final float JIGGLE_SCALE = 0.92f;

    // =========================================================================
    // 5. SETTLING THRESHOLDS
    // =========================================================================

    public static final double EPSILON_POSITION_PX = 0.5;
    public static final double EPSILON_VELOCITY_PX_S = 1.0;
}
