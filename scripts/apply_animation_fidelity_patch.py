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

    # 1. QuickstepAppTransitionManagerImpl.smali: Pin launch DragLayer alpha to 1.0f (no black void)
    p1 = os.path.join(root, r"smali_classes3\com\android\launcher3\QuickstepAppTransitionManagerImpl.smali")
    
    old1_alpha = """:array_0
    .array-data 4
        0x3f800000    # 1.0f
        0x0
    .end array-data"""
    new1_alpha = """:array_0
    .array-data 4
        0x3f800000    # 1.0f
        0x3f800000    # 1.0f
    .end array-data"""
    all_ok &= patch_file(p1, old1_alpha, new1_alpha, "Pin DragLayer alpha to 1.0f (eliminate black void)")

    old1_dur = """.field private static final APP_LAUNCH_DURATION:J = 0x1c2L"""
    new1_dur = """.field private static final APP_LAUNCH_DURATION:J = 0x1f4L"""
    all_ok &= patch_file(p1, old1_dur, new1_dur, "Update APP_LAUNCH_DURATION to 500ms")

    old1_compat = """    :cond_0
    const-wide/16 v3, 0x1c2"""
    new1_compat = """    :cond_0
    const-wide/16 v3, 0x1f4"""
    all_ok &= patch_file(p1, old1_compat, new1_compat, "RemoteAnimationAdapterCompat 500ms duration synchronization")

    # 2. FloatingIconView.smali: Remove 10% shape reveal clamp (toMax = 1.0f)
    p2 = os.path.join(root, r"smali_classes3\com\android\launcher3\views\FloatingIconView.smali")
    old2_tomax = """    if-eqz p6, :cond_1

    const/high16 v9, 0x41200000    # 10.0f

    move v13, v9

    goto :goto_1"""
    new2_tomax = """    if-eqz p6, :cond_1

    const/high16 v9, 0x3f800000    # 1.0f

    move v13, v9

    goto :goto_1"""
    all_ok &= patch_file(p2, old2_tomax, new2_tomax, "Remove 10% shape reveal clamp (toMax=1.0f)")

    # 3. FloatingIconView.smali: Synchronous icon fallback and frame-0 visibility
    old2_sync = """    .line 575
    invoke-direct {p0, p1}, Lcom/android/launcher3/views/FloatingIconView;->hideOriginalView(Landroid/view/View;)V

    goto :goto_0

    .line 577
    :cond_1
    iget-object v2, p0, Lcom/android/launcher3/views/FloatingIconView;->mIconLoadResult:Lcom/android/launcher3/views/FloatingIconView$IconLoadResult;"""

    new2_sync = """    .line 575
    invoke-direct {p0, p1}, Lcom/android/launcher3/views/FloatingIconView;->hideOriginalView(Landroid/view/View;)V

    const/4 v2, 0x0

    invoke-virtual {p0, v2}, Lcom/android/launcher3/views/FloatingIconView;->setVisibility(I)V

    goto :goto_0

    .line 577
    :cond_1
    instance-of v2, p1, Lcom/android/launcher3/BubbleTextView;

    if-eqz v2, :cond_skip_sync

    move-object v2, p1

    check-cast v2, Lcom/android/launcher3/BubbleTextView;

    invoke-virtual {v2}, Lcom/android/launcher3/BubbleTextView;->getIcon()Landroid/graphics/drawable/Drawable;

    move-result-object v2

    if-eqz v2, :cond_skip_sync

    const/4 v3, 0x0

    const/4 v4, 0x0

    invoke-direct {p0, p1, v2, v3, v4}, Lcom/android/launcher3/views/FloatingIconView;->setIcon(Landroid/view/View;Landroid/graphics/drawable/Drawable;Landroid/graphics/drawable/Drawable;I)V

    invoke-direct {p0, p1}, Lcom/android/launcher3/views/FloatingIconView;->hideOriginalView(Landroid/view/View;)V

    const/4 v2, 0x0

    invoke-virtual {p0, v2}, Lcom/android/launcher3/views/FloatingIconView;->setVisibility(I)V

    :cond_skip_sync
    iget-object v2, p0, Lcom/android/launcher3/views/FloatingIconView;->mIconLoadResult:Lcom/android/launcher3/views/FloatingIconView$IconLoadResult;"""
    all_ok &= patch_file(p2, old2_sync, new2_sync, "Synchronous BubbleTextView fallback & frame 0 visibility")

    old2_anim_start = """.method public onAnimationStart(Landroid/animation/Animator;)V
    .locals 1
    .param p1, "animator"    # Landroid/animation/Animator;

    .line 686
    iget-object v0, p0, Lcom/android/launcher3/views/FloatingIconView;->mIconLoadResult:Lcom/android/launcher3/views/FloatingIconView$IconLoadResult;

    if-eqz v0, :cond_0

    iget-boolean v0, v0, Lcom/android/launcher3/views/FloatingIconView$IconLoadResult;->isIconLoaded:Z

    if-eqz v0, :cond_0

    .line 687
    const/4 v0, 0x0

    invoke-virtual {p0, v0}, Lcom/android/launcher3/views/FloatingIconView;->setVisibility(I)V

    .line 689
    :cond_0"""

    new2_anim_start = """.method public onAnimationStart(Landroid/animation/Animator;)V
    .locals 1
    .param p1, "animator"    # Landroid/animation/Animator;

    .line 686
    const/4 v0, 0x0

    invoke-virtual {p0, v0}, Lcom/android/launcher3/views/FloatingIconView;->setVisibility(I)V

    .line 689
    :cond_0"""
    all_ok &= patch_file(p2, old2_anim_start, new2_anim_start, "Unconditional visibility on onAnimationStart")

    # 4. WindowTransformSwipeHandler.smali: Bypass screenshotTask on swipe-to-home
    p3 = os.path.join(root, r"smali_classes3\com\android\quickstep\WindowTransformSwipeHandler.smali")
    old3_snap = """    if-eqz v1, :cond_4

    .line 1110
    iget-object v2, p0, Lcom/android/quickstep/WindowTransformSwipeHandler;->mTaskSnapshot:Lcom/android/systemui/shared/recents/model/ThumbnailData;

    if-nez v2, :cond_2

    .line 1111
    iget v2, p0, Lcom/android/quickstep/WindowTransformSwipeHandler;->mRunningTaskId:I

    invoke-virtual {v1, v2}, Lcom/android/quickstep/util/SwipeAnimationTargetSet;->screenshotTask(I)Lcom/android/systemui/shared/recents/model/ThumbnailData;

    move-result-object v2

    iput-object v2, p0, Lcom/android/quickstep/WindowTransformSwipeHandler;->mTaskSnapshot:Lcom/android/systemui/shared/recents/model/ThumbnailData;

    .line 1114
    :cond_2
    iget-object v2, p0, Lcom/android/quickstep/WindowTransformSwipeHandler;->mGestureEndTarget:Lcom/android/quickstep/WindowTransformSwipeHandler$GestureEndTarget;

    sget-object v3, Lcom/android/quickstep/WindowTransformSwipeHandler$GestureEndTarget;->HOME:Lcom/android/quickstep/WindowTransformSwipeHandler$GestureEndTarget;

    if-ne v2, v3, :cond_3

    .line 1117
    const/4 v2, 0x0

    .local v2, "taskView":Lcom/android/quickstep/views/TaskView;
    goto :goto_0"""

    new3_snap = """    if-eqz v1, :cond_4

    iget-object v2, p0, Lcom/android/quickstep/WindowTransformSwipeHandler;->mGestureEndTarget:Lcom/android/quickstep/WindowTransformSwipeHandler$GestureEndTarget;

    sget-object v3, Lcom/android/quickstep/WindowTransformSwipeHandler$GestureEndTarget;->HOME:Lcom/android/quickstep/WindowTransformSwipeHandler$GestureEndTarget;

    if-ne v2, v3, :cond_skip_home

    const/4 v2, 0x0

    goto :goto_0

    :cond_skip_home
    .line 1110
    iget-object v2, p0, Lcom/android/quickstep/WindowTransformSwipeHandler;->mTaskSnapshot:Lcom/android/systemui/shared/recents/model/ThumbnailData;

    if-nez v2, :cond_2

    .line 1111
    iget v2, p0, Lcom/android/quickstep/WindowTransformSwipeHandler;->mRunningTaskId:I

    invoke-virtual {v1, v2}, Lcom/android/quickstep/util/SwipeAnimationTargetSet;->screenshotTask(I)Lcom/android/systemui/shared/recents/model/ThumbnailData;

    move-result-object v2

    iput-object v2, p0, Lcom/android/quickstep/WindowTransformSwipeHandler;->mTaskSnapshot:Lcom/android/systemui/shared/recents/model/ThumbnailData;

    .line 1114
    :cond_2
    iget-object v2, p0, Lcom/android/quickstep/WindowTransformSwipeHandler;->mRecentsView:Lcom/android/quickstep/views/RecentsView;"""
    all_ok &= patch_file(p3, old3_snap, new3_snap, "Bypass screenshotTask when target is HOME")

    if all_ok:
        print("\n[SUCCESS] All animation fidelity patches verified and applied successfully!")
        return 0
    else:
        print("\n[FAILURE] Some patches failed to apply or verify.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
