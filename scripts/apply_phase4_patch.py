import sys
import os

def patch_file(path, old_text, new_text, desc):
    if not os.path.exists(path):
        print(f"ERROR: File not found: {path}")
        return False
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if old_text not in content:
        if new_text in content:
            print(f"ALREADY PATCHED: {desc} in {path}")
            return True
        print(f"ERROR: Could not find target in {path} for {desc}")
        return False
    content = content.replace(old_text, new_text, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"SUCCESS: Patched {desc} in {path}")
    return True

def main():
    root = r"c:\mad\launcher3_src"
    all_ok = True

    # 1. QuickstepAppTransitionManagerImpl.smali: closing duration from 250ms (0xfa) to 400ms (0x190)
    p1 = os.path.join(root, r"smali_classes3\com\android\launcher3\QuickstepAppTransitionManagerImpl.smali")
    old1 = """    invoke-static {v0}, Landroid/animation/ValueAnimator;->ofFloat([F)Landroid/animation/ValueAnimator;

    move-result-object v7

    .line 662
    .local v7, "closingAnimator":Landroid/animation/ValueAnimator;
    const/16 v8, 0xfa"""
    new1 = """    invoke-static {v0}, Landroid/animation/ValueAnimator;->ofFloat([F)Landroid/animation/ValueAnimator;

    move-result-object v7

    .line 662
    .local v7, "closingAnimator":Landroid/animation/ValueAnimator;
    const/16 v8, 0x190"""
    all_ok &= patch_file(p1, old1, new1, "Programmatic exit duration (400ms)")

    # 2. QuickstepAppTransitionManagerImpl$8.smali: scale and alpha spring transitions
    p2 = os.path.join(root, r"smali_classes3\com\android\launcher3\QuickstepAppTransitionManagerImpl$8.smali")
    old2 = """    new-instance v9, Lcom/android/quickstep/util/MultiValueUpdateListener$FloatProp;

    iget-object v0, v7, Lcom/android/launcher3/QuickstepAppTransitionManagerImpl$8;->this$0:Lcom/android/launcher3/QuickstepAppTransitionManagerImpl;

    invoke-static {v0}, Lcom/android/launcher3/QuickstepAppTransitionManagerImpl;->access$400(Lcom/android/launcher3/QuickstepAppTransitionManagerImpl;)F

    move-result v3

    iget v0, v7, Lcom/android/launcher3/QuickstepAppTransitionManagerImpl$8;->val$duration:I

    int-to-float v5, v0

    sget-object v6, Lcom/android/launcher3/anim/Interpolators;->DEACCEL_1_7:Landroid/view/animation/Interpolator;

    const/4 v2, 0x0

    const/4 v4, 0x0

    move-object v0, v9

    move-object v1, p0

    invoke-direct/range {v0 .. v6}, Lcom/android/quickstep/util/MultiValueUpdateListener$FloatProp;-><init>(Lcom/android/quickstep/util/MultiValueUpdateListener;FFFFLandroid/view/animation/Interpolator;)V

    iput-object v9, v7, Lcom/android/launcher3/QuickstepAppTransitionManagerImpl$8;->mDy:Lcom/android/quickstep/util/MultiValueUpdateListener$FloatProp;

    .line 668
    new-instance v9, Lcom/android/quickstep/util/MultiValueUpdateListener$FloatProp;

    iget v0, v7, Lcom/android/launcher3/QuickstepAppTransitionManagerImpl$8;->val$duration:I

    int-to-float v5, v0

    sget-object v6, Lcom/android/launcher3/anim/Interpolators;->DEACCEL_1_7:Landroid/view/animation/Interpolator;

    const/high16 v2, 0x3f800000    # 1.0f

    const/high16 v3, 0x3f800000    # 1.0f

    move-object v0, v9

    invoke-direct/range {v0 .. v6}, Lcom/android/quickstep/util/MultiValueUpdateListener$FloatProp;-><init>(Lcom/android/quickstep/util/MultiValueUpdateListener;FFFFLandroid/view/animation/Interpolator;)V

    iput-object v9, v7, Lcom/android/launcher3/QuickstepAppTransitionManagerImpl$8;->mScale:Lcom/android/quickstep/util/MultiValueUpdateListener$FloatProp;

    .line 669
    new-instance v9, Lcom/android/quickstep/util/MultiValueUpdateListener$FloatProp;

    sget-object v6, Lcom/android/launcher3/anim/Interpolators;->LINEAR:Landroid/view/animation/Interpolator;

    const/4 v3, 0x0

    const/high16 v4, 0x41c80000    # 25.0f

    const/high16 v5, 0x42fa0000    # 125.0f

    move-object v0, v9

    invoke-direct/range {v0 .. v6}, Lcom/android/quickstep/util/MultiValueUpdateListener$FloatProp;-><init>(Lcom/android/quickstep/util/MultiValueUpdateListener;FFFFLandroid/view/animation/Interpolator;)V

    iput-object v9, v7, Lcom/android/launcher3/QuickstepAppTransitionManagerImpl$8;->mAlpha:Lcom/android/quickstep/util/MultiValueUpdateListener$FloatProp;"""

    new2 = """    new-instance v9, Lcom/android/quickstep/util/MultiValueUpdateListener$FloatProp;

    iget-object v0, v7, Lcom/android/launcher3/QuickstepAppTransitionManagerImpl$8;->this$0:Lcom/android/launcher3/QuickstepAppTransitionManagerImpl;

    invoke-static {v0}, Lcom/android/launcher3/QuickstepAppTransitionManagerImpl;->access$400(Lcom/android/launcher3/QuickstepAppTransitionManagerImpl;)F

    move-result v3

    iget v0, v7, Lcom/android/launcher3/QuickstepAppTransitionManagerImpl$8;->val$duration:I

    int-to-float v5, v0

    new-instance v6, Lcom/android/launcher3/anim/Interpolators$6;

    invoke-direct {v6}, Lcom/android/launcher3/anim/Interpolators$6;-><init>()V

    const/4 v2, 0x0

    const/4 v4, 0x0

    move-object v0, v9

    move-object v1, p0

    invoke-direct/range {v0 .. v6}, Lcom/android/quickstep/util/MultiValueUpdateListener$FloatProp;-><init>(Lcom/android/quickstep/util/MultiValueUpdateListener;FFFFLandroid/view/animation/Interpolator;)V

    iput-object v9, v7, Lcom/android/launcher3/QuickstepAppTransitionManagerImpl$8;->mDy:Lcom/android/quickstep/util/MultiValueUpdateListener$FloatProp;

    .line 668
    new-instance v9, Lcom/android/quickstep/util/MultiValueUpdateListener$FloatProp;

    iget v0, v7, Lcom/android/launcher3/QuickstepAppTransitionManagerImpl$8;->val$duration:I

    int-to-float v5, v0

    new-instance v6, Lcom/android/launcher3/anim/Interpolators$6;

    invoke-direct {v6}, Lcom/android/launcher3/anim/Interpolators$6;-><init>()V

    const/high16 v2, 0x3f800000    # 1.0f

    const v3, 0x3f6147ae    # 0.88f (iOS app exit scale)

    move-object v0, v9

    invoke-direct/range {v0 .. v6}, Lcom/android/quickstep/util/MultiValueUpdateListener$FloatProp;-><init>(Lcom/android/quickstep/util/MultiValueUpdateListener;FFFFLandroid/view/animation/Interpolator;)V

    iput-object v9, v7, Lcom/android/launcher3/QuickstepAppTransitionManagerImpl$8;->mScale:Lcom/android/quickstep/util/MultiValueUpdateListener$FloatProp;

    .line 669
    new-instance v9, Lcom/android/quickstep/util/MultiValueUpdateListener$FloatProp;

    sget-object v6, Lcom/android/launcher3/anim/Interpolators;->FAST_OUT_SLOW_IN:Landroid/view/animation/Interpolator;

    const/high16 v2, 0x3f800000    # 1.0f

    const/4 v3, 0x0

    const/high16 v4, 0x42f00000    # 120.0f

    const/high16 v5, 0x438c0000    # 280.0f

    move-object v0, v9

    invoke-direct/range {v0 .. v6}, Lcom/android/quickstep/util/MultiValueUpdateListener$FloatProp;-><init>(Lcom/android/quickstep/util/MultiValueUpdateListener;FFFFLandroid/view/animation/Interpolator;)V

    iput-object v9, v7, Lcom/android/launcher3/QuickstepAppTransitionManagerImpl$8;->mAlpha:Lcom/android/quickstep/util/MultiValueUpdateListener$FloatProp;"""
    all_ok &= patch_file(p2, old2, new2, "Programmatic exit scale spring and alpha cross-fade")

    # 3. RectFSpringAnim.smali: Y spring velocity preservation and scale spring alignment
    p3 = os.path.join(root, r"smali_classes3\com\android\quickstep\util\RectFSpringAnim.smali")
    old3_vel = """    invoke-static {v15}, Ljava/lang/Math;->abs(F)F

    move-result v0

    const v1, 0x3f666666    # 0.9f

    mul-float/2addr v0, v1

    const v1, 0x469c4000    # 20000.0f

    div-float/2addr v0, v1

    const v1, 0x3dcccccd    # 0.1f

    add-float v18, v0, v1"""
    new3_vel = """    const/high16 v18, 0x3f800000    # 1.0f (full iOS gesture velocity preservation)"""
    all_ok &= patch_file(p3, old3_vel, new3_vel, "Preserve 100% gesture fling velocity")

    old3_scale = """    new-instance v3, Landroidx/dynamicanimation/animation/SpringForce;

    invoke-direct {v3, v1}, Landroidx/dynamicanimation/animation/SpringForce;-><init>(F)V

    const/high16 v4, 0x3f400000    # 0.75f

    .line 171
    invoke-virtual {v3, v4}, Landroidx/dynamicanimation/animation/SpringForce;->setDampingRatio(F)Landroidx/dynamicanimation/animation/SpringForce;

    move-result-object v3

    const/high16 v4, 0x43480000    # 200.0f

    .line 172
    invoke-virtual {v3, v4}, Landroidx/dynamicanimation/animation/SpringForce;->setStiffness(F)Landroidx/dynamicanimation/animation/SpringForce;

    move-result-object v3

    .line 170
    invoke-virtual {v2, v3}, Landroidx/dynamicanimation/animation/SpringAnimation;->setSpring(Landroidx/dynamicanimation/animation/SpringForce;)Landroidx/dynamicanimation/animation/SpringAnimation;

    move-result-object v2

    iget v3, v12, Landroid/graphics/PointF;->y:F

    mul-float/2addr v3, v0"""
    new3_scale = """    new-instance v3, Landroidx/dynamicanimation/animation/SpringForce;

    invoke-direct {v3, v1}, Landroidx/dynamicanimation/animation/SpringForce;-><init>(F)V

    const v4, 0x3f51eb85    # 0.82f (iOS damping ratio)

    .line 171
    invoke-virtual {v3, v4}, Landroidx/dynamicanimation/animation/SpringForce;->setDampingRatio(F)Landroidx/dynamicanimation/animation/SpringForce;

    move-result-object v3

    const/high16 v4, 0x43430000    # 195.0f (iOS stiffness T0=0.45s)

    .line 172
    invoke-virtual {v3, v4}, Landroidx/dynamicanimation/animation/SpringForce;->setStiffness(F)Landroidx/dynamicanimation/animation/SpringForce;

    move-result-object v3

    .line 170
    invoke-virtual {v2, v3}, Landroidx/dynamicanimation/animation/SpringAnimation;->setSpring(Landroidx/dynamicanimation/animation/SpringForce;)Landroidx/dynamicanimation/animation/SpringAnimation;

    move-result-object v2

    iget v3, v12, Landroid/graphics/PointF;->y:F

    const/high16 v4, -0x3b860000    # -1000.0f

    mul-float/2addr v3, v4

    mul-float/2addr v3, v0"""
    all_ok &= patch_file(p3, old3_scale, new3_scale, "Align scale spring to iOS parameters and correct start velocity")

    # 4. FlingSpringAnim.smali: update spring stiffness and damping
    p4 = os.path.join(root, r"smali_classes3\com\android\launcher3\anim\FlingSpringAnim.smali")
    old4_const = """.field private static final SPRING_DAMPING:F = 0.8f

.field private static final SPRING_STIFFNESS:F = 200.0f"""
    new4_const = """.field private static final SPRING_DAMPING:F = 0.82f

.field private static final SPRING_STIFFNESS:F = 195.0f"""
    all_ok &= patch_file(p4, old4_const, new4_const, "FlingSpringAnim constants")

    old4_params = """    const/high16 v2, 0x43480000    # 200.0f

    invoke-virtual {v1, v2}, Landroidx/dynamicanimation/animation/SpringForce;->setStiffness(F)Landroidx/dynamicanimation/animation/SpringForce;

    move-result-object v1

    .line 58
    const v2, 0x3f4ccccd    # 0.8f

    invoke-virtual {v1, v2}, Landroidx/dynamicanimation/animation/SpringForce;->setDampingRatio(F)Landroidx/dynamicanimation/animation/SpringForce;"""
    new4_params = """    const/high16 v2, 0x43430000    # 195.0f

    invoke-virtual {v1, v2}, Landroidx/dynamicanimation/animation/SpringForce;->setStiffness(F)Landroidx/dynamicanimation/animation/SpringForce;

    move-result-object v1

    .line 58
    const v2, 0x3f51eb85    # 0.82f

    invoke-virtual {v1, v2}, Landroidx/dynamicanimation/animation/SpringForce;->setDampingRatio(F)Landroidx/dynamicanimation/animation/SpringForce;"""
    all_ok &= patch_file(p4, old4_params, new4_params, "FlingSpringAnim spring parameters")

    # 5. FloatingIconView.smali: synchronize foreground spring parallax
    p5 = os.path.join(root, r"smali_classes3\com\android\launcher3\views\FloatingIconView.smali")
    old5 = """    const/high16 v2, 0x3f400000    # 0.75f

    invoke-virtual {v1, v2}, Landroidx/dynamicanimation/animation/SpringForce;->setDampingRatio(F)Landroidx/dynamicanimation/animation/SpringForce;

    move-result-object v1

    .line 183
    const/high16 v3, 0x43480000    # 200.0f

    invoke-virtual {v1, v3}, Landroidx/dynamicanimation/animation/SpringForce;->setStiffness(F)Landroidx/dynamicanimation/animation/SpringForce;"""
    new5 = """    const v2, 0x3f51eb85    # 0.82f

    invoke-virtual {v1, v2}, Landroidx/dynamicanimation/animation/SpringForce;->setDampingRatio(F)Landroidx/dynamicanimation/animation/SpringForce;

    move-result-object v1

    .line 183
    const/high16 v3, 0x43430000    # 195.0f

    invoke-virtual {v1, v3}, Landroidx/dynamicanimation/animation/SpringForce;->setStiffness(F)Landroidx/dynamicanimation/animation/SpringForce;"""
    all_ok &= patch_file(p5, old5, new5, "FloatingIconView foreground parallax spring")

    # 6. BaseSwipeUpHandler.smali: anchor endRadius to squircle 36px
    p6 = os.path.join(root, r"smali_classes3\com\android\quickstep\BaseSwipeUpHandler.smali")
    old6 = """    invoke-virtual {v14}, Landroid/graphics/RectF;->width()F

    move-result v0

    const/high16 v1, 0x40c00000    # 6.0f

    div-float v17, v0, v1"""
    new6 = """    const/high16 v17, 0x42100000    # 36.0f (icon squircle corner radius)"""
    all_ok &= patch_file(p6, old6, new6, "BaseSwipeUpHandler endRadius anchor to 36px")

    # 7. WindowTransformSwipeHandler.smali: overview threshold from 0.7f to 0.38f
    p7 = os.path.join(root, r"smali_classes3\com\android\quickstep\WindowTransformSwipeHandler.smali")
    old7_1 = """    iget-object v3, p0, Lcom/android/quickstep/WindowTransformSwipeHandler;->mCurrentShift:Lcom/android/quickstep/AnimatedFloat;

    iget v3, v3, Lcom/android/quickstep/AnimatedFloat;->value:F

    const v4, 0x3f333333    # 0.7f

    cmpl-float v3, v3, v4"""
    new7_1 = """    iget-object v3, p0, Lcom/android/quickstep/WindowTransformSwipeHandler;->mCurrentShift:Lcom/android/quickstep/AnimatedFloat;

    iget v3, v3, Lcom/android/quickstep/AnimatedFloat;->value:F

    const v4, 0x3ec28f5c    # 0.38f

    cmpl-float v3, v3, v4"""
    all_ok &= patch_file(p7, old7_1, new7_1, "WindowTransformSwipeHandler calculateEndTarget threshold (0.38f)")

    old7_2 = """    iget-object v1, p0, Lcom/android/quickstep/WindowTransformSwipeHandler;->mCurrentShift:Lcom/android/quickstep/AnimatedFloat;

    iget v1, v1, Lcom/android/quickstep/AnimatedFloat;->value:F

    const v2, 0x3f333333    # 0.7f

    cmpl-float v1, v1, v2"""
    new7_2 = """    iget-object v1, p0, Lcom/android/quickstep/WindowTransformSwipeHandler;->mCurrentShift:Lcom/android/quickstep/AnimatedFloat;

    iget v1, v1, Lcom/android/quickstep/AnimatedFloat;->value:F

    const v2, 0x3ec28f5c    # 0.38f

    cmpl-float v1, v1, v2"""
    all_ok &= patch_file(p7, old7_2, new7_2, "WindowTransformSwipeHandler mPassedOverviewThreshold (0.38f)")

    # 8. Create Interpolators$6.smali linking to IOSMotionEngine.getAppExitInterpolation
    p8 = os.path.join(root, r"smali_classes3\com\android\launcher3\anim\Interpolators$6.smali")
    interp6_content = """.class public Lcom/android/launcher3/anim/Interpolators$6;
.super Ljava/lang/Object;
.source "Interpolators.java"

# interfaces
.implements Landroid/view/animation/Interpolator;


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lcom/android/launcher3/anim/Interpolators;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x1
    name = null
.end annotation


# direct methods
.method public constructor <init>()V
    .locals 0

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public getInterpolation(F)F
    .locals 1
    .param p1, "t"    # F

    invoke-static {p1}, Lcom/ios/motion/IOSMotionEngine;->getAppExitInterpolation(F)F

    move-result v0

    return v0
.end method
"""
    if not os.path.exists(p8):
        with open(p8, "w", encoding="utf-8") as f:
            f.write(interp6_content)
        print(f"SUCCESS: Created {p8}")
    else:
        print(f"ALREADY PRESENT: {p8}")

    # 9. StaggeredWorkspaceAnim.smali: neutralize vertical workspace jiggle
    p9 = os.path.join(root, r"smali_classes3\com\android\quickstep\util\StaggeredWorkspaceAnim.smali")
    old9_1 = """    invoke-virtual {v0, v1}, Landroid/content/res/Resources;->getDimensionPixelSize(I)I

    move-result v0

    int-to-float v0, v0

    iput v0, v11, Lcom/android/quickstep/util/StaggeredWorkspaceAnim;->mSpringTransY:F"""
    new9_1 = """    invoke-virtual {v0, v1}, Landroid/content/res/Resources;->getDimensionPixelSize(I)I

    move-result v0

    int-to-float v0, v0

    const/4 v0, 0x0

    iput v0, v11, Lcom/android/quickstep/util/StaggeredWorkspaceAnim;->mSpringTransY:F"""
    all_ok &= patch_file(p9, old9_1, new9_1, "StaggeredWorkspaceAnim mSpringTransY to 0")

    old9_2 = """.method private addStaggeredAnimationForView(Landroid/view/View;II)V
    .locals 10
    .param p1, "v"    # Landroid/view/View;
    .param p2, "row"    # I
    .param p3, "totalRows"    # I"""
    new9_2 = """.method private addStaggeredAnimationForView(Landroid/view/View;II)V
    .locals 0
    .param p1, "v"    # Landroid/view/View;
    .param p2, "row"    # I
    .param p3, "totalRows"    # I

    return-void
.end method"""
    with open(p9, "r", encoding="utf-8") as f:
        p9_content = f.read()
    if new9_2 in p9_content:
        print(f"ALREADY PATCHED: StaggeredWorkspaceAnim addStaggeredAnimationForView neutralization in {p9}")
    elif old9_2 in p9_content:
        # Replace the entire old method up to .end method
        idx = p9_content.find(old9_2)
        end_idx = p9_content.find(".end method", idx)
        if end_idx != -1:
            full_old = p9_content[idx:end_idx + len(".end method")]
            p9_content = p9_content.replace(full_old, new9_2, 1)
            with open(p9, "w", encoding="utf-8") as f:
                f.write(p9_content)
            print(f"SUCCESS: Patched StaggeredWorkspaceAnim addStaggeredAnimationForView neutralization in {p9}")
        else:
            print("ERROR: Could not find .end method for addStaggeredAnimationForView")
            all_ok = False
    else:
        print(f"ERROR: Could not find target for addStaggeredAnimationForView in {p9}")
        all_ok = False

    print(f"\nOverall patch status: {'ALL SUCCESS' if all_ok else 'SOME FAILED'}")
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
