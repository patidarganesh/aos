package com.ios.motion;

/**
 * Analytic second-order ordinary differential equation solver for damped harmonic motion:
 *   m * x''(t) + c * x'(t) + k * x(t) = 0
 *
 * Implements the exact analytic solutions for:
 *   - Underdamped  (zeta < 1.0)
 *   - Critically damped (zeta == 1.0)
 *   - Overdamped   (zeta > 1.0)
 */
public final class SpringSolver {

    public static final class SpringState {
        public double position;
        public double velocity;

        public SpringState(double position, double velocity) {
            this.position = position;
            this.velocity = velocity;
        }
    }

    private final double mass;
    private final double stiffness;
    private final double damping;
    private final double omega0;       // sqrt(k / m)
    private final double zeta;         // c / (2 * sqrt(k * m))
    private final double omegaD;       // omega0 * sqrt(1 - zeta^2) (for underdamped)
    private final double omegaStar;    // omega0 * sqrt(zeta^2 - 1) (for overdamped)

    /**
     * Constructs a SpringSolver with raw physical parameters.
     * @param mass mass in kg (usually 1.0)
     * @param stiffness spring constant k in N/m
     * @param damping viscous damping coefficient c in Ns/m
     */
    public SpringSolver(double mass, double stiffness, double damping) {
        if (mass <= 0.0) throw new IllegalArgumentException("Mass must be positive");
        if (stiffness <= 0.0) throw new IllegalArgumentException("Stiffness must be positive");
        if (damping < 0.0) throw new IllegalArgumentException("Damping must be non-negative");

        this.mass = mass;
        this.stiffness = stiffness;
        this.damping = damping;

        this.omega0 = Math.sqrt(stiffness / mass);
        this.zeta = damping / (2.0 * Math.sqrt(stiffness * mass));

        if (zeta < 1.0) {
            this.omegaD = omega0 * Math.sqrt(1.0 - (zeta * zeta));
            this.omegaStar = 0.0;
        } else if (zeta > 1.0) {
            this.omegaD = 0.0;
            this.omegaStar = omega0 * Math.sqrt((zeta * zeta) - 1.0);
        } else {
            this.omegaD = 0.0;
            this.omegaStar = 0.0;
        }
    }

    /**
     * Factory constructor using UIKit-style perceptual parameters:
     * @param response period of undamped oscillation in seconds (T0 = 2*pi / omega0)
     * @param dampingRatio damping ratio zeta (1.0 = critically damped, <1.0 = bouncier)
     */
    public static SpringSolver fromPerceptual(double response, double dampingRatio) {
        if (response <= 0.0) throw new IllegalArgumentException("Response must be positive");
        if (dampingRatio < 0.0) throw new IllegalArgumentException("Damping ratio cannot be negative");

        double mass = 1.0;
        double omega0 = (2.0 * Math.PI) / response;
        double stiffness = omega0 * omega0 * mass;
        double damping = 2.0 * dampingRatio * Math.sqrt(stiffness * mass);
        return new SpringSolver(mass, stiffness, damping);
    }

    /**
     * Solves the position and velocity at time t given initial displacement and initial velocity.
     * Target equilibrium is 0.0. (If target is non-zero, pass x0 = current - target, then add target to result).
     *
     * @param t time in seconds (t >= 0)
     * @param x0 initial displacement from equilibrium
     * @param v0 initial velocity (e.g. gesture release velocity)
     * @return SpringState containing position and velocity at time t
     */
    public SpringState solve(double t, double x0, double v0) {
        if (t <= 0.0) {
            return new SpringState(x0, v0);
        }

        double position;
        double velocity;

        if (zeta < 0.999999) {
            // Underdamped
            double envelope = Math.exp(-zeta * omega0 * t);
            double c1 = x0;
            double c2 = (v0 + (zeta * omega0 * x0)) / omegaD;

            double cosPart = Math.cos(omegaD * t);
            double sinPart = Math.sin(omegaD * t);

            position = envelope * (c1 * cosPart + c2 * sinPart);
            velocity = -zeta * omega0 * position + envelope * (-c1 * omegaD * sinPart + c2 * omegaD * cosPart);

        } else if (zeta > 1.000001) {
            // Overdamped
            double c1 = (v0 + (zeta * omega0 + omegaStar) * x0) / (2.0 * omegaStar);
            double c2 = x0 - c1;

            double expPos = Math.exp((-zeta * omega0 + omegaStar) * t);
            double expNeg = Math.exp((-zeta * omega0 - omegaStar) * t);

            position = c1 * expPos + c2 * expNeg;
            velocity = c1 * (-zeta * omega0 + omegaStar) * expPos + c2 * (-zeta * omega0 - omegaStar) * expNeg;

        } else {
            // Critically damped
            double envelope = Math.exp(-omega0 * t);
            double c1 = x0;
            double c2 = v0 + omega0 * x0;

            position = envelope * (c1 + c2 * t);
            velocity = -omega0 * position + envelope * c2;
        }

        return new SpringState(position, velocity);
    }

    /**
     * Estimates the settling duration in seconds when both |position| < epsilonPos and |velocity| < epsilonVel.
     */
    public double calculateSettlingDuration(double x0, double v0, double epsilonPos, double epsilonVel) {
        if (Math.abs(x0) < epsilonPos && Math.abs(v0) < epsilonVel) {
            return 0.0;
        }

        // Numerical search with analytic upper bound
        double step = 0.016; // 60fps frame delta
        double maxTime = 3.0; // max 3 seconds timeout
        double t = 0.0;
        double settleStart = -1.0;

        while (t < maxTime) {
            SpringState state = solve(t, x0, v0);
            if (Math.abs(state.position) < epsilonPos && Math.abs(state.velocity) < epsilonVel) {
                if (settleStart < 0.0) {
                    settleStart = t;
                } else if (t - settleStart > 0.08) { // confirmed settled for 5 frames
                    return settleStart;
                }
            } else {
                settleStart = -1.0;
            }
            t += step;
        }

        return maxTime;
    }

    public double getMass() { return mass; }
    public double getStiffness() { return stiffness; }
    public double getDamping() { return damping; }
    public double getOmega0() { return omega0; }
    public double getZeta() { return zeta; }
}
