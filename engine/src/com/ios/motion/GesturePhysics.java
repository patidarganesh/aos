package com.ios.motion;

/**
 * Handles fluid gesture physics including non-linear rubber banding,
 * velocity smoothing, and directional gesture gating.
 */
public final class GesturePhysics {

    public static final double DEFAULT_RUBBER_BAND_COEFFICIENT = 0.55;

    private GesturePhysics() {}

    /**
     * Calculates the non-linear rubber band resistive offset when dragging beyond limits.
     * Formula:
     *   offset = (1.0 - (1.0 / ((distance * c / dimension) + 1.0))) * dimension
     *
     * @param distance raw displacement past the boundary (positive)
     * @param dimension reference view dimension (e.g. screen height or width)
     * @param coefficient resistance coefficient (default ~0.55)
     * @return dampened resistive offset
     */
    public static double rubberBandClamp(double distance, double dimension, double coefficient) {
        if (distance <= 0.0 || dimension <= 0.0) {
            return 0.0;
        }
        return (1.0 - (1.0 / (((distance * coefficient) / dimension) + 1.0))) * dimension;
    }

    public static double rubberBandClamp(double distance, double dimension) {
        return rubberBandClamp(distance, dimension, DEFAULT_RUBBER_BAND_COEFFICIENT);
    }

    /**
     * Inverse of rubberBandClamp: Given a rubber-banded offset, computes what the raw gesture distance was.
     */
    public static double invertRubberBand(double offset, double dimension, double coefficient) {
        if (offset <= 0.0 || dimension <= 0.0 || offset >= dimension) {
            return 0.0;
        }
        return (offset * dimension) / (coefficient * (dimension - offset));
    }

    /**
     * Determines whether a gesture is predominantly vertical vs horizontal.
     * @param deltaX raw X movement
     * @param deltaY raw Y movement
     * @param verticalBiasRatio factor by which Y must exceed X (e.g. 1.5 for Spotlight)
     * @return true if gesture is classified as vertical
     */
    public static boolean isVerticalGesture(float deltaX, float deltaY, float verticalBiasRatio) {
        return Math.abs(deltaY) > Math.abs(deltaX) * verticalBiasRatio;
    }

    /**
     * Compensates for touch slop by blending smoothly from 0 after slop is breached,
     * avoiding an abrupt visual jump on the frame where touch slop is passed.
     */
    public static float blendSlop(float rawDelta, float touchSlop) {
        float absDelta = Math.abs(rawDelta);
        if (absDelta <= touchSlop) {
            return 0.0f;
        }
        return Math.signum(rawDelta) * (absDelta - touchSlop);
    }
}
