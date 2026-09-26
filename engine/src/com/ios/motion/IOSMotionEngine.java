package com.ios.motion;

import android.view.View;

/**
 * IOSMotionEngine: Unified motion coordinator for system transitions.
 * Provides centralized spring solver instances, physics calculators,
 * and view animation helpers.
 */
public final class IOSMotionEngine {

    private static volatile IOSMotionEngine sInstance;

    // Cached Solvers for High Frequency Transitions
    private final SpringSolver appLaunchSolver;
    private final SpringSolver appExitSolver;
    private final SpringSolver workspacePageSolver;
    private final SpringSolver spotlightSolver;
    private final SpringSolver recentsSnapSolver;
    private final SpringSolver folderSolver;
    private final SpringSolver systemUIPanelSolver;
    private final SpringSolver sliderBounceSolver;

    private IOSMotionEngine() {
        this.appLaunchSolver = SpringSolver.fromPerceptual(MotionConfig.APP_LAUNCH_RESPONSE, MotionConfig.APP_LAUNCH_DAMPING_RATIO);
        this.appExitSolver = SpringSolver.fromPerceptual(MotionConfig.APP_EXIT_RESPONSE, MotionConfig.APP_EXIT_DAMPING_RATIO);
        this.workspacePageSolver = SpringSolver.fromPerceptual(MotionConfig.WORKSPACE_PAGE_RESPONSE, MotionConfig.WORKSPACE_PAGE_DAMPING_RATIO);
        this.spotlightSolver = SpringSolver.fromPerceptual(MotionConfig.SPOTLIGHT_RESPONSE, MotionConfig.SPOTLIGHT_DAMPING_RATIO);
        this.recentsSnapSolver = SpringSolver.fromPerceptual(MotionConfig.RECENTS_SNAP_RESPONSE, MotionConfig.RECENTS_SNAP_DAMPING_RATIO);
        this.folderSolver = SpringSolver.fromPerceptual(MotionConfig.FOLDER_TRANSITION_RESPONSE, MotionConfig.FOLDER_TRANSITION_DAMPING_RATIO);
        this.systemUIPanelSolver = SpringSolver.fromPerceptual(MotionConfig.SYSTEMUI_PANEL_RESPONSE, MotionConfig.SYSTEMUI_PANEL_DAMPING_RATIO);
        this.sliderBounceSolver = SpringSolver.fromPerceptual(MotionConfig.SLIDER_BOUNCE_RESPONSE, MotionConfig.SLIDER_BOUNCE_DAMPING_RATIO);
    }

    public static IOSMotionEngine getInstance() {
        if (sInstance == null) {
            synchronized (IOSMotionEngine.class) {
                if (sInstance == null) {
                    sInstance = new IOSMotionEngine();
                }
            }
        }
        return sInstance;
    }

    // Factory methods
    public SpringSolver createCustomSpring(double response, double dampingRatio) {
        return SpringSolver.fromPerceptual(response, dampingRatio);
    }

    public SpringSolver getAppLaunchSolver() { return appLaunchSolver; }
    public SpringSolver getAppExitSolver() { return appExitSolver; }
    public SpringSolver getWorkspacePageSolver() { return workspacePageSolver; }
    public SpringSolver getSpotlightSolver() { return spotlightSolver; }
    public SpringSolver getRecentsSnapSolver() { return recentsSnapSolver; }
    public SpringSolver getFolderSolver() { return folderSolver; }
    public SpringSolver getSystemUIPanelSolver() { return systemUIPanelSolver; }
    public SpringSolver getSliderBounceSolver() { return sliderBounceSolver; }

    /**
     * High-speed static spring interpolation for Workspace page transitions.
     * Evaluates damped harmonic spring at t = input * MotionConfig.WORKSPACE_PAGE_RESPONSE.
     */
    public static float getWorkspacePageInterpolation(float input) {
        if (input <= 0.0f) return 0.0f;
        if (input >= 1.0f) return 1.0f;
        IOSMotionEngine engine = getInstance();
        double t = input * MotionConfig.WORKSPACE_PAGE_RESPONSE;
        SpringSolver.SpringState state = engine.workspacePageSolver.solve(t, -1.0, 0.0);
        return (float) (1.0 + state.position);
    }

    /**
     * High-speed static spring interpolation for App Launch transitions.
     */
    public static float getAppLaunchInterpolation(float input) {
        if (input <= 0.0f) return 0.0f;
        if (input >= 1.0f) return 1.0f;
        IOSMotionEngine engine = getInstance();
        double t = input * MotionConfig.APP_LAUNCH_RESPONSE;
        SpringSolver.SpringState state = engine.appLaunchSolver.solve(t, -1.0, 0.0);
        return (float) (1.0 + state.position);
    }

    /**
     * High-speed static spring interpolation for App Exit / Home transitions.
     */
    public static float getAppExitInterpolation(float input) {
        if (input <= 0.0f) return 0.0f;
        if (input >= 1.0f) return 1.0f;
        IOSMotionEngine engine = getInstance();
        double t = input * MotionConfig.APP_EXIT_RESPONSE;
        SpringSolver.SpringState state = engine.appExitSolver.solve(t, -1.0, 0.0);
        return (float) (1.0 + state.position);
    }

    /**
     * Creates a Choreographer-driven spring transition controller.
     */
    public TransitionController createTransition(TransitionController.OnSpringUpdateListener listener) {
        return new TransitionController(listener);
    }

    /**
     * Convenience method to animate translationY with spring physics and velocity handoff.
     */
    public TransitionController animateTranslationY(final View target, double targetY, double velocityY, SpringSolver solver) {
        if (target == null) return null;

        TransitionController controller = new TransitionController(new TransitionController.OnSpringUpdateListener() {
            @Override
            public void onSpringUpdate(TransitionController ctrl, double currentPosition, double currentVelocity) {
                target.setTranslationY((float) currentPosition);
            }

            @Override
            public void onSpringEnd(TransitionController ctrl, double finalPosition) {
                target.setTranslationY((float) finalPosition);
            }
        });

        controller.start(solver, target.getTranslationY(), targetY, velocityY);
        return controller;
    }

    /**
     * Convenience method to animate translationX with spring physics and velocity handoff.
     */
    public TransitionController animateTranslationX(final View target, double targetX, double velocityX, SpringSolver solver) {
        if (target == null) return null;

        TransitionController controller = new TransitionController(new TransitionController.OnSpringUpdateListener() {
            @Override
            public void onSpringUpdate(TransitionController ctrl, double currentPosition, double currentVelocity) {
                target.setTranslationX((float) currentPosition);
            }

            @Override
            public void onSpringEnd(TransitionController ctrl, double finalPosition) {
                target.setTranslationX((float) finalPosition);
            }
        });

        controller.start(solver, target.getTranslationX(), targetX, velocityX);
        return controller;
    }
}
