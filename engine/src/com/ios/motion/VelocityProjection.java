package com.ios.motion;

/**
 * Predicts resting position and deceleration curves from touch release velocity,
 * matching UIScrollView deceleration physics.
 */
public final class VelocityProjection {

    // UIScrollView standard deceleration rate (0.996 per millisecond)
    public static final double DECELERATION_RATE_NORMAL = 0.996;
    public static final double DECELERATION_RATE_FAST = 0.990;

    // Decay rate lambda = -1000 * ln(decelerationRate)
    public static final double LAMBDA_NORMAL = -1000.0 * Math.log(DECELERATION_RATE_NORMAL); // ~4.008 s^-1

    private VelocityProjection() {}

    /**
     * Predicts the resting point after momentum deceleration:
     *   x_final = x0 + (v0 / lambda)
     *
     * @param initialPosition current position at release
     * @param initialVelocity velocity in pixels/second
     * @return projected final resting position
     */
    public static double predictRestingPosition(double initialPosition, double initialVelocity) {
        return initialPosition + (initialVelocity / LAMBDA_NORMAL);
    }

    /**
     * Determines whether a transition should commit to destination or abort back to origin,
     * considering both displacement progress and projected momentum.
     *
     * @param currentPosition current position [0.0 to destination]
     * @param destination target position (e.g. 1.0 or screen height)
     * @param velocity velocity along gesture axis (pixels/sec)
     * @param distanceThreshold fraction of distance required to commit (e.g. 0.45)
     * @param flingVelocityThreshold velocity in px/s that forces commit regardless of distance
     * @return true to commit, false to abort
     */
    public static boolean shouldCommitTransition(
            double currentPosition,
            double destination,
            double velocity,
            double distanceThreshold,
            double flingVelocityThreshold) {

        double distance = Math.abs(destination);
        if (distance <= 0.0001) return true;

        double progress = Math.abs(currentPosition) / distance;

        // Fling forward forcefully
        if (velocity > flingVelocityThreshold) {
            return true;
        }
        // Fling backward forcefully
        if (velocity < -flingVelocityThreshold) {
            return false;
        }

        // Projected landing check
        double projected = predictRestingPosition(currentPosition, velocity);
        double projectedProgress = Math.abs(projected) / distance;

        return projectedProgress >= distanceThreshold || progress >= distanceThreshold;
    }
}
