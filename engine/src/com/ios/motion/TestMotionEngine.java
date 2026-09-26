package com.ios.motion;

public class TestMotionEngine {

    public static void main(String[] args) {
        System.out.println("Running IOSMotionEngine Verification Suite...");

        testSpringSolverUnderdamped();
        testSpringSolverCriticallyDamped();
        testSettlingDuration();
        testRubberBanding();
        testVelocityProjection();

        System.out.println("ALL TESTS PASSED! Motion Engine Mathematics Verified.");
    }

    private static void testSpringSolverUnderdamped() {
        System.out.print("Testing Underdamped SpringSolver... ");
        // response = 0.5s, zeta = 0.8
        SpringSolver solver = SpringSolver.fromPerceptual(0.5, 0.8);
        assert solver.getZeta() < 1.0 : "Must be underdamped";

        // Initial displacement 100px, initial velocity 0
        SpringSolver.SpringState s0 = solver.solve(0.0, 100.0, 0.0);
        assert Math.abs(s0.position - 100.0) < 1e-6 : "Initial position mismatch";
        assert Math.abs(s0.velocity - 0.0) < 1e-6 : "Initial velocity mismatch";

        // At t = 0.25s, position must have decreased significantly towards 0
        SpringSolver.SpringState sMid = solver.solve(0.25, 100.0, 0.0);
        assert sMid.position < 30.0 : "Spring should be moving toward 0";

        // At t = 1.0s, spring should be settled near 0
        SpringSolver.SpringState sLate = solver.solve(1.0, 100.0, 0.0);
        assert Math.abs(sLate.position) < 0.5 : "Spring should be settled at 1s";

        System.out.println("PASS");
    }

    private static void testSpringSolverCriticallyDamped() {
        System.out.print("Testing Critically Damped SpringSolver... ");
        SpringSolver solver = SpringSolver.fromPerceptual(0.4, 1.0);
        assert Math.abs(solver.getZeta() - 1.0) < 1e-5 : "Must be critically damped";

        SpringSolver.SpringState s = solver.solve(0.5, 200.0, 0.0);
        assert s.position > 0.0 && s.position < 20.0 : "Monotonic decay without oscillation";
        System.out.println("PASS");
    }

    private static void testSettlingDuration() {
        System.out.print("Testing Settling Duration Calculation... ");
        SpringSolver solver = SpringSolver.fromPerceptual(0.45, 0.82);
        double duration = solver.calculateSettlingDuration(100.0, 500.0, 0.5, 1.0);
        assert duration > 0.2 && duration < 1.5 : "Settling duration should be reasonable: " + duration;
        System.out.println("PASS (Settling time: " + String.format("%.3fs", duration) + ")");
    }

    private static void testRubberBanding() {
        System.out.print("Testing Rubber Banding Physics... ");
        double dim = 1000.0;
        double r0 = GesturePhysics.rubberBandClamp(0.0, dim);
        assert r0 == 0.0 : "Zero displacement must yield zero offset";

        double r100 = GesturePhysics.rubberBandClamp(100.0, dim);
        double r500 = GesturePhysics.rubberBandClamp(500.0, dim);
        double r2000 = GesturePhysics.rubberBandClamp(2000.0, dim);

        assert r100 > 0.0 : "Offset must be positive";
        assert r500 > r100 : "Offset must increase monotonically";
        assert r2000 > r500 : "Offset must increase monotonically";
        assert r2000 < dim : "Offset must asymptotically stay below dimension";

        // Derivative must be decreasing (concave down)
        double slope1 = (r100 - r0) / 100.0;
        double slope2 = (r500 - r100) / 400.0;
        assert slope1 > slope2 : "Instantaneous resistance must increase with displacement";

        System.out.println("PASS (r100=" + String.format("%.1f", r100) + ", r500=" + String.format("%.1f", r500) + ")");
    }

    private static void testVelocityProjection() {
        System.out.print("Testing Velocity Projection... ");
        double x0 = 100.0;
        double v0 = 1000.0; // px/s
        double resting = VelocityProjection.predictRestingPosition(x0, v0);
        assert resting > x0 : "Resting position should project forward";
        double expected = x0 + (1000.0 / VelocityProjection.LAMBDA_NORMAL);
        assert Math.abs(resting - expected) < 1e-4 : "Projected position formula mismatch";

        boolean commitForward = VelocityProjection.shouldCommitTransition(50.0, 200.0, 600.0, 0.5, 450.0);
        assert commitForward : "High velocity forward should commit";

        boolean abortBackward = VelocityProjection.shouldCommitTransition(150.0, 200.0, -600.0, 0.5, 450.0);
        assert !abortBackward : "High velocity backward should abort";

        System.out.println("PASS (projected=" + String.format("%.1f", resting) + ")");
    }
}
