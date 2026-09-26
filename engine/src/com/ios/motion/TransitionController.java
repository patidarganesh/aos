package com.ios.motion;

import android.view.Choreographer;

/**
 * High-performance frame-pacing transition coordinator.
 * Synchronizes spring calculations directly with Android's Choreographer vsync pulses,
 * avoiding object allocations on the UI thread during active frames.
 */
public final class TransitionController implements Choreographer.FrameCallback {

    public interface OnSpringUpdateListener {
        void onSpringUpdate(TransitionController controller, double currentPosition, double currentVelocity);
        void onSpringEnd(TransitionController controller, double finalPosition);
    }

    private SpringSolver solver;
    private double startPosition;
    private double targetPosition;
    private double initialVelocity;
    private double currentPosition;
    private double currentVelocity;
    private double startTimeNanos = -1;
    private boolean isRunning = false;

    private final OnSpringUpdateListener listener;

    public TransitionController(OnSpringUpdateListener listener) {
        this.listener = listener;
    }

    /**
     * Starts an interactive spring settling transition.
     *
     * @param solver the SpringSolver configured with desired response and damping
     * @param fromPosition starting position
     * @param toPosition target destination
     * @param initialVelocity velocity in units/second at gesture release
     */
    public void start(SpringSolver solver, double fromPosition, double toPosition, double initialVelocity) {
        cancel();

        this.solver = solver;
        this.startPosition = fromPosition;
        this.targetPosition = toPosition;
        this.initialVelocity = initialVelocity;
        this.currentPosition = fromPosition;
        this.currentVelocity = initialVelocity;
        this.startTimeNanos = -1;
        this.isRunning = true;

        Choreographer.getInstance().postFrameCallback(this);
    }

    public void cancel() {
        if (isRunning) {
            isRunning = false;
            Choreographer.getInstance().removeFrameCallback(this);
        }
    }

    @Override
    public void doFrame(long frameTimeNanos) {
        if (!isRunning || solver == null) {
            return;
        }

        if (startTimeNanos < 0) {
            startTimeNanos = frameTimeNanos;
        }

        double tSeconds = (frameTimeNanos - startTimeNanos) / 1_000_000_000.0;
        double displacement0 = startPosition - targetPosition;

        // Solve relative to 0 equilibrium
        SpringSolver.SpringState state = solver.solve(tSeconds, displacement0, initialVelocity);
        currentPosition = targetPosition + state.position;
        currentVelocity = state.velocity;

        // Check settling condition
        boolean settled = Math.abs(state.position) <= MotionConfig.EPSILON_POSITION_PX
                && Math.abs(state.velocity) <= MotionConfig.EPSILON_VELOCITY_PX_S
                && tSeconds > 0.05; // minimum 3 frames

        if (settled) {
            isRunning = false;
            currentPosition = targetPosition;
            currentVelocity = 0.0;
            if (listener != null) {
                listener.onSpringUpdate(this, currentPosition, currentVelocity);
                listener.onSpringEnd(this, targetPosition);
            }
        } else {
            if (listener != null) {
                listener.onSpringUpdate(this, currentPosition, currentVelocity);
            }
            if (isRunning) {
                Choreographer.getInstance().postFrameCallback(this);
            }
        }
    }

    public boolean isRunning() { return isRunning; }
    public double getCurrentPosition() { return currentPosition; }
    public double getCurrentVelocity() { return currentVelocity; }
}
