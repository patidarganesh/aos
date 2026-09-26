# App Library Specification & Interaction Dynamics

## 1. Hierarchy & Structure
* Located on the rightmost workspace page.
* Search bar at top ("App Library" search).
* 2x2 Category Collections:
  - Each category box displays up to 3 full-size launchable icons and 1 mini 2x2 folder cluster.
  - Tapping full-size icon launches app directly.
  - Tapping mini 2x2 cluster expands the category into full view.
* Pull-down or search tap opens alphabetical A-Z list view with scrubber on right edge.

## 2. Transition Mechanics
* Swiping from final icon page to App Library follows normal horizontal spring paging.
* Pulling down inside App Library smoothly transitions into the alphabetical list with list items sliding in with staggered spring delays ($\Delta t = 12\text{ ms}$ per row).
* Alphabet scrubber on right handles rapid touch scrub with haptic ticks and magnified letter popover.
