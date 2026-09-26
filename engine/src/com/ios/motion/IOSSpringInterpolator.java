package com.ios.motion;

import android.animation.TimeInterpolator;

/**
 * Android TimeInterpolator adapter for the analytic iOS spring solver.
 * Maps normalized input fraction u in [0, 1] to physically accurate spring progression.
 */
public class IOSSpringInterpolator implements TimeInterpolator {

    private final SpringSolver solver;
    private final double durationSeconds;
    private final double initialVelocityNormalized;

    /**
     * @param response undamped cycle period in seconds
     * @param dampingRatio damping ratio zeta
     * @param durationSeconds total animator duration in seconds
     * @param initialVelocityNormalized initial velocity scaled by (velocity_px_s / total_distance_px)
     */
    public IOSSpringInterpolator(double response, double dampingRatio, double durationSeconds, double initialVelocityNormalized) {
        this.solver = SpringSolver.fromPerceptual(response, dampingRatio);
        this.durationSeconds = durationSeconds > 0.0 ? durationSeconds : 0.45;
        this.initialVelocityNormalized = initialVelocityNormalized;
    }

    public IOSSpringInterpolator(double response, double dampingRatio, double durationSeconds) {
        this(response, dampingRatio, durationSeconds, 0.0);
    }

    public IOSSpringInterpolator(double response, double dampingRatio) {
        this(response, dampingRatio, response * 1.2, 0.0);
    }

    @Override
    public float getInterpolation(float input) {
        if (input <= 0.0f) return 0.0f;
        if (input >= 1.0f) return 1.0f;

        double t = input * durationSeconds;
        // Start from -1.0 to 0.0 equilibrium
        SpringSolver.SpringState state = solver.solve(t, -1.0, initialVelocityNormalized);
        float value = (float) (1.0 + state.position);
        return value;
    }

    public SpringSolver getSolver() {
        return solver;
    }

    public double getDurationSeconds() {
        return durationSeconds;
    }
}
