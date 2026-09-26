package com.ios.motion;

/**
 * Continuous time deceleration model for momentum flings.
 */
public final class DecelerationModel {

    private final double lambda;

    public DecelerationModel(double decelerationRate) {
        this.lambda = -1000.0 * Math.log(decelerationRate);
    }

    public DecelerationModel() {
        this(VelocityProjection.DECELERATION_RATE_NORMAL);
    }

    /**
     * Calculates position at time t (seconds) from release.
     *   x(t) = x0 + (v0 / lambda) * (1 - e^(-lambda * t))
     */
    public double getPosition(double t, double x0, double v0) {
        if (t <= 0.0) return x0;
        return x0 + (v0 / lambda) * (1.0 - Math.exp(-lambda * t));
    }

    /**
     * Calculates velocity at time t (seconds) from release.
     *   v(t) = v0 * e^(-lambda * t)
     */
    public double getVelocity(double t, double v0) {
        if (t <= 0.0) return v0;
        return v0 * Math.exp(-lambda * t);
    }

    public double getLambda() {
        return lambda;
    }
}
