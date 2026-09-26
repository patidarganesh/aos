import os
import sys

def apply_patch():
    root = r"c:\mad\launcher3_src\smali_classes3"
    
    # 1. PagedView.smali
    paged_view_path = os.path.join(root, r"com\android\launcher3\PagedView.smali")
    print(f"[*] Patching {paged_view_path}...")
    with open(paged_view_path, "r", encoding="utf-8") as f:
        pv_content = f.read()
    
    # Target 1: Overscroll boundary guard in onTouchEvent
    old_pv_boundary = """    iget-boolean v6, v0, Lcom/android/launcher3/PagedView;->mFreeScroll:Z

    if-nez v6, :cond_18

    move/from16 v18, v2

    invoke-virtual/range {p0 .. p0}, Lcom/android/launcher3/PagedView;->getScrollX()I

    move-result v2

    iget v5, v0, Lcom/android/launcher3/PagedView;->mMinScrollX:I

    if-ge v2, v5, :cond_check_max

    const/4 v2, 0x0

    invoke-virtual {v0, v2, v10}, Lcom/android/launcher3/PagedView;->snapToPageWithVelocity(II)Z

    goto/16 :goto_9

    :cond_check_max
    iget v5, v0, Lcom/android/launcher3/PagedView;->mMaxScrollX:I

    if-le v2, v5, :cond_normal_paging

    invoke-virtual/range {p0 .. p0}, Lcom/android/launcher3/PagedView;->getChildCount()I

    move-result v2

    add-int/lit8 v2, v2, -0x1

    invoke-virtual {v0, v2, v10}, Lcom/android/launcher3/PagedView;->snapToPageWithVelocity(II)Z

    goto/16 :goto_9

    :cond_normal_paging"""

    new_pv_boundary = """    iget-boolean v6, v0, Lcom/android/launcher3/PagedView;->mFreeScroll:Z

    if-nez v6, :cond_18

    move/from16 v18, v2

    invoke-virtual/range {p0 .. p0}, Lcom/android/launcher3/PagedView;->getUnboundedScrollX()I

    move-result v2

    iget v5, v0, Lcom/android/launcher3/PagedView;->mMinScrollX:I

    if-ge v2, v5, :cond_check_max

    const/4 v2, 0x0

    const/16 v5, 0x17c

    invoke-virtual {v0, v2, v5}, Lcom/android/launcher3/PagedView;->snapToPage(II)Z

    goto/16 :goto_9

    :cond_check_max
    iget v5, v0, Lcom/android/launcher3/PagedView;->mMaxScrollX:I

    if-le v2, v5, :cond_check_p0_drag

    invoke-virtual/range {p0 .. p0}, Lcom/android/launcher3/PagedView;->getChildCount()I

    move-result v2

    add-int/lit8 v2, v2, -0x1

    const/16 v5, 0x17c

    invoke-virtual {v0, v2, v5}, Lcom/android/launcher3/PagedView;->snapToPage(II)Z

    goto/16 :goto_9

    :cond_check_p0_drag
    iget v2, v0, Lcom/android/launcher3/PagedView;->mCurrentPage:I

    if-nez v2, :cond_check_plast_drag

    if-lez v11, :cond_check_plast_drag

    const/4 v2, 0x0

    const/16 v5, 0x17c

    invoke-virtual {v0, v2, v5}, Lcom/android/launcher3/PagedView;->snapToPage(II)Z

    goto/16 :goto_9

    :cond_check_plast_drag
    invoke-virtual/range {p0 .. p0}, Lcom/android/launcher3/PagedView;->getChildCount()I

    move-result v5

    add-int/lit8 v5, v5, -0x1

    if-ne v2, v5, :cond_normal_paging

    if-gez v11, :cond_normal_paging

    const/16 v2, 0x17c

    invoke-virtual {v0, v5, v2}, Lcom/android/launcher3/PagedView;->snapToPage(II)Z

    goto/16 :goto_9

    :cond_normal_paging"""

    if old_pv_boundary in pv_content:
        pv_content = pv_content.replace(old_pv_boundary, new_pv_boundary)
        print("  [+] PagedView overscroll boundary guard updated.")
    else:
        print("  [!] PagedView overscroll boundary guard pattern NOT found!")
        sys.exit(1)

    # Target 2: isInOverScroll() using getUnboundedScrollX()
    old_isin_overscroll = """.method protected isInOverScroll()Z
    .locals 2

    .line 1406
    .local p0, "this":Lcom/android/launcher3/PagedView;, "Lcom/android/launcher3/PagedView<TT;>;"
    invoke-virtual {p0}, Lcom/android/launcher3/PagedView;->getScrollX()I

    move-result v0

    iget v1, p0, Lcom/android/launcher3/PagedView;->mMaxScrollX:I

    if-gt v0, v1, :cond_1

    invoke-virtual {p0}, Lcom/android/launcher3/PagedView;->getScrollX()I

    move-result v0

    iget v1, p0, Lcom/android/launcher3/PagedView;->mMinScrollX:I

    if-ge v0, v1, :cond_0

    goto :goto_0

    :cond_0
    const/4 v0, 0x0

    goto :goto_1

    :cond_1
    :goto_0
    const/4 v0, 0x1

    :goto_1
    return v0
.end method"""

    new_isin_overscroll = """.method protected isInOverScroll()Z
    .locals 2

    .line 1406
    .local p0, "this":Lcom/android/launcher3/PagedView;, "Lcom/android/launcher3/PagedView<TT;>;"
    invoke-virtual {p0}, Lcom/android/launcher3/PagedView;->getUnboundedScrollX()I

    move-result v0

    iget v1, p0, Lcom/android/launcher3/PagedView;->mMaxScrollX:I

    if-gt v0, v1, :cond_1

    invoke-virtual {p0}, Lcom/android/launcher3/PagedView;->getUnboundedScrollX()I

    move-result v0

    iget v1, p0, Lcom/android/launcher3/PagedView;->mMinScrollX:I

    if-ge v0, v1, :cond_0

    goto :goto_0

    :cond_0
    const/4 v0, 0x0

    goto :goto_1

    :cond_1
    :goto_0
    const/4 v0, 0x1

    :goto_1
    return v0
.end method"""

    if old_isin_overscroll in pv_content:
        pv_content = pv_content.replace(old_isin_overscroll, new_isin_overscroll)
        print("  [+] PagedView.isInOverScroll() updated to getUnboundedScrollX().")
    else:
        print("  [!] PagedView.isInOverScroll() pattern NOT found!")
        sys.exit(1)

    # Target 3: getPageSnapDuration()
    old_snap_dur = """.method protected getPageSnapDuration()I
    .locals 1

    .line 1410
    .local p0, "this":Lcom/android/launcher3/PagedView;, "Lcom/android/launcher3/PagedView<TT;>;"
    invoke-virtual {p0}, Lcom/android/launcher3/PagedView;->isInOverScroll()Z

    move-result v0

    if-eqz v0, :cond_0

    .line 1411
    const/16 v0, 0x10e

    return v0

    .line 1413
    :cond_0
    const/16 v0, 0x2ee

    return v0
.end method"""

    new_snap_dur = """.method protected getPageSnapDuration()I
    .locals 1

    .line 1410
    .local p0, "this":Lcom/android/launcher3/PagedView;, "Lcom/android/launcher3/PagedView<TT;>;"
    invoke-virtual {p0}, Lcom/android/launcher3/PagedView;->isInOverScroll()Z

    move-result v0

    if-eqz v0, :cond_0

    .line 1411
    const/16 v0, 0x17c

    return v0

    .line 1413
    :cond_0
    const/16 v0, 0x17c

    return v0
.end method"""

    if old_snap_dur in pv_content:
        pv_content = pv_content.replace(old_snap_dur, new_snap_dur)
        print("  [+] PagedView.getPageSnapDuration() updated to 380ms (0x17c).")
    else:
        print("  [!] PagedView.getPageSnapDuration() pattern NOT found!")
        sys.exit(1)

    with open(paged_view_path, "w", encoding="utf-8") as f:
        f.write(pv_content)

    # 2. TaskCornerRadius.smali
    tcr_path = os.path.join(root, r"com\android\quickstep\util\TaskCornerRadius.smali")
    print(f"[*] Patching {tcr_path}...")
    with open(tcr_path, "r", encoding="utf-8") as f:
        tcr_content = f.read()

    old_tcr_get = """.method public static get(Landroid/content/Context;)F
    .locals 2
    .param p0, "context"    # Landroid/content/Context;

    .line 28
    invoke-virtual {p0}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    invoke-static {v0}, Lcom/android/systemui/shared/system/QuickStepContract;->supportsRoundedCornersOnWindows(Landroid/content/res/Resources;)Z

    move-result v0

    if-eqz v0, :cond_0

    .line 29
    invoke-static {p0}, Lcom/android/launcher3/util/Themes;->getDialogCornerRadius(Landroid/content/Context;)F

    move-result v0

    goto :goto_0

    .line 30
    :cond_0
    invoke-virtual {p0}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    sget v1, Lcom/android/launcher3/R$dimen;->task_corner_radius_small:I

    invoke-virtual {v0, v1}, Landroid/content/res/Resources;->getDimension(I)F

    move-result v0

    .line 28
    :goto_0
    return v0
.end method"""

    new_tcr_get = """.method public static get(Landroid/content/Context;)F
    .locals 1
    .param p0, "context"    # Landroid/content/Context;

    const/high16 v0, 0x42100000    # 36.0f

    return v0
.end method"""

    if old_tcr_get in tcr_content:
        tcr_content = tcr_content.replace(old_tcr_get, new_tcr_get)
        print("  [+] TaskCornerRadius.get() updated to return 36.0f squircle radius.")
    else:
        print("  [!] TaskCornerRadius.get() pattern NOT found!")
        sys.exit(1)

    with open(tcr_path, "w", encoding="utf-8") as f:
        f.write(tcr_content)

    # 3. TaskView.smali
    tv_path = os.path.join(root, r"com\android\quickstep\views\TaskView.smali")
    print(f"[*] Patching {tv_path}...")
    with open(tv_path, "r", encoding="utf-8") as f:
        tv_content = f.read()

    old_tv_curve = """.method private static getCurveScaleForCurveInterpolation(F)F
    .locals 2
    .param p0, "curveInterpolation"    # F

    .line 587
    const v0, 0x3cf5c28f    # 0.03f

    mul-float/2addr v0, p0

    const/high16 v1, 0x3f800000    # 1.0f

    sub-float/2addr v1, v0

    return v1
.end method"""

    new_tv_curve = """.method private static getCurveScaleForCurveInterpolation(F)F
    .locals 2
    .param p0, "curveInterpolation"    # F

    .line 587
    const v0, 0x3df5c28f    # 0.12f

    mul-float/2addr v0, p0

    const/high16 v1, 0x3f800000    # 1.0f

    sub-float/2addr v1, v0

    return v1
.end method"""

    if old_tv_curve in tv_content:
        tv_content = tv_content.replace(old_tv_curve, new_tv_curve)
        print("  [+] TaskView depth scale updated to 0.12f (0.88 scale deck cascade).")
    else:
        print("  [!] TaskView depth scale pattern NOT found!")
        sys.exit(1)

    with open(tv_path, "w", encoding="utf-8") as f:
        f.write(tv_content)

    print("[SUCCESS] All Phase 5 & Rubber-Band patches applied successfully!")

if __name__ == "__main__":
    apply_patch()
