////////////////////////////////////////////////////////////////
// ARCM_m2 @ 0021c2ac  size=68
// callers: FUN_001867a8@001867a8 
// callees: 

int ARCM_m2(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  iVar1 = *(int *)(*(int *)(param_1 + 4) + 0x38);
  iVar2 = *(int *)(param_1 + 4) + iVar1 * 0x10;
  if ((-1 < iVar1) && (iVar1 = *(int *)(iVar2 + 4), iVar1 != 0)) {
    iVar3 = *(int *)(iVar2 + 8) - iVar1 >> 2;
  }
  return iVar3;
}


////////////////////////////////////////////////////////////////
// ARCM_m3 @ 0021c248  size=100
// callers: FUN_001867a8@001867a8 
// callees: 

undefined4 ARCM_m3(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = 0;
  iVar1 = *(int *)(*(int *)(param_1 + 4) + 0x38);
  if ((-1 < iVar1) && (-1 < param_2)) {
    iVar2 = *(int *)(param_1 + 4) + iVar1 * 0x10;
    iVar1 = *(int *)(iVar2 + 4);
    if ((iVar1 != 0) && (param_2 < *(int *)(iVar2 + 8) - iVar1 >> 2)) {
      uVar3 = *(undefined4 *)(param_2 * 4 + iVar1);
    }
  }
  return uVar3;
}


////////////////////////////////////////////////////////////////
// ARSR_m0 @ 0018f260  size=256
// callers: 
// callees: FUN_00a8af48@00a8af48 FUN_00a9c30c@00a9c30c 

void ARSR_m0(undefined4 *param_1)

{
  undefined4 *puVar1;
  
  *param_1 = &PTR_PTR_ARSR_m0_016c6938;
  param_1[0x14] = &PTR_PTR_LAB_016c77e8;
  param_1[0x67] = &PTR_PTR_LAB_016c4dd0;
  param_1[0x6c] = &PTR_PTR_LAB_016c4dd0;
  param_1[0x15] = &PTR_PTR_LAB_016c7848;
  puVar1 = (undefined4 *)param_1[0x66];
  if (puVar1 != (undefined4 *)0x0) {
    (*(code *)**(undefined4 **)*puVar1)(puVar1,param_1[0x65]);
    param_1[0x65] = 0;
    param_1[0x66] = 0;
  }
  param_1[0x14] = &PTR_PTR_LAB_016c6a48;
  param_1[0x15] = &PTR_PTR_LAB_016c6a20;
  FUN_00a9c30c(param_1 + 4);
  FUN_00a8af48(param_1 + 3);
  *param_1 = &PTR_PTR_LAB_016c5498;
  return;
}


////////////////////////////////////////////////////////////////
// 00190bd8: no function (creating)
// ARSR_m1 @ 00190bd8  size=264
// callers: 
// callees: FUN_00a8af48@00a8af48 FUN_00a9c30c@00a9c30c FUN_00bbcc84@00bbcc84 

void ARSR_m1(undefined4 *param_1)

{
  undefined4 *puVar1;
  
  *param_1 = &PTR_PTR_ARSR_m0_016c6938;
  param_1[0x14] = &PTR_PTR_LAB_016c77e8;
  param_1[0x67] = &PTR_PTR_LAB_016c4dd0;
  param_1[0x6c] = &PTR_PTR_LAB_016c4dd0;
  param_1[0x15] = &PTR_PTR_LAB_016c7848;
  puVar1 = (undefined4 *)param_1[0x66];
  if (puVar1 != (undefined4 *)0x0) {
    (*(code *)**(undefined4 **)*puVar1)(puVar1,param_1[0x65]);
    param_1[0x65] = 0;
    param_1[0x66] = 0;
  }
  param_1[0x14] = &PTR_PTR_LAB_016c6a48;
  param_1[0x15] = &PTR_PTR_LAB_016c6a20;
  FUN_00a9c30c(param_1 + 4);
  FUN_00a8af48(param_1 + 3);
  *param_1 = &PTR_PTR_LAB_016c5498;
  FUN_00bbcc84(param_1);
  return;
}


////////////////////////////////////////////////////////////////
// 001913e8: no function (creating)
// ARSR_m2 @ 001913e8  size=344
// callers: 
// callees: FUN_00a8af48@00a8af48 FUN_00abbde0@00abbde0 FUN_0019c974@0019c974 FUN_0019c130@0019c130 FUN_0019c1a8@0019c1a8 FUN_00a8ae60@00a8ae60 FUN_00abbf28@00abbf28 FUN_00190e4c@00190e4c 

void ARSR_m2(int param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 *puVar1;
  int iVar2;
  int *piVar3;
  int iVar4;
  undefined1 auStack_50 [4];
  undefined1 auStack_4c [8];
  undefined1 auStack_44 [12];
  
  FUN_00abbf28(param_1 + 0x10);
  iVar2 = *(int *)(param_1 + 8);
  FUN_00a8ae60(auStack_44,param_1 + 0xc);
  if (iVar2 != 0) {
    iVar4 = param_1 + 0x50;
    FUN_0019c130(iVar4);
    FUN_0019c974(iVar4,param_2,param_3);
    FUN_0019c1a8(iVar4);
    FUN_00190e4c(iVar2,param_2,param_3);
    piVar3 = DAT_01807ab4;
    puVar1 = *(undefined4 **)(*DAT_01807ab4 + 0x20);
    FUN_00a8ae60(auStack_4c,param_1 + 0xc);
    (*(code *)*puVar1)(piVar3,auStack_50);
    FUN_00a8af48(auStack_4c);
  }
  FUN_00a8af48(auStack_44);
  FUN_00abbde0(param_1 + 0x10);
  return;
}


////////////////////////////////////////////////////////////////
// 0018f0f0: no function (creating)
// ARSR_m3 @ 0018f0f0  size=300
// callers: 
// callees: FUN_00a8af48@00a8af48 FUN_00abbde0@00abbde0 FUN_00a8ae60@00a8ae60 FUN_0018eec0@0018eec0 FUN_00abbf28@00abbf28 

void ARSR_m3(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  int *piVar3;
  undefined1 auStack_50 [4];
  undefined1 auStack_4c [8];
  undefined1 auStack_44 [12];
  
  FUN_00abbf28(param_1 + 0x10);
  iVar2 = *(int *)(param_1 + 8);
  FUN_00a8ae60(auStack_44,param_1 + 0xc);
  if (iVar2 != 0) {
    FUN_0018eec0(iVar2,param_2,param_3,param_4);
    piVar3 = DAT_01807ab4;
    puVar1 = *(undefined4 **)(*DAT_01807ab4 + 0x20);
    FUN_00a8ae60(auStack_4c,param_1 + 0xc);
    (*(code *)*puVar1)(piVar3,auStack_50);
    FUN_00a8af48(auStack_4c);
  }
  FUN_00a8af48(auStack_44);
  FUN_00abbde0(param_1 + 0x10);
  return;
}


////////////////////////////////////////////////////////////////
// 0018e544: no function (creating)
// ARSR_m6 @ 0018e544  size=660
// callers: 
// callees: FUN_008f610c@008f610c FUN_008f5e74@008f5e74 FUN_00837f44@00837f44 FUN_008f6054@008f6054 FUN_008f5f60@008f5f60 FUN_008f5ecc@008f5ecc FUN_00198ae0@00198ae0 

void ARSR_m6(undefined8 param_1,undefined4 *param_2,int *param_3)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  int iVar4;
  undefined4 *puVar5;
  char cVar7;
  uint uVar6;
  ulonglong uVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  undefined1 auStack_130 [4];
  undefined1 auStack_12c [4];
  undefined1 auStack_128 [8];
  undefined1 auStack_120 [16];
  undefined1 auStack_110 [16];
  float fStack_100;
  undefined1 auStack_f8 [24];
  undefined1 auStack_e0 [80];
  
  piVar1 = (int *)(*(code *)**(undefined4 **)(*param_3 + 0x40))(param_3);
  if (piVar1 != (int *)0x0) {
    uVar8 = 0;
    do {
      iVar9 = 0;
      piVar2 = (int *)(*(code *)**(undefined4 **)(*piVar1 + 8))(piVar1,uVar8 & 0xffffffff);
      if (piVar2 != (int *)0x0) {
        for (; uVar6 = (*(code *)**(undefined4 **)(*piVar2 + 0x20))(piVar2),
            iVar9 < (int)(uVar6 & 0xff); iVar9 = iVar9 + 1) {
          piVar3 = (int *)(*(code *)**(undefined4 **)(*piVar2 + 0x3c))(piVar2,iVar9);
          iVar4 = (*(code *)**(undefined4 **)(*piVar3 + 8))(piVar3);
          if (0 < iVar4) {
            iVar10 = 0;
            do {
              puVar5 = (undefined4 *)FUN_00837f44(*param_2);
              FUN_00198ae0(auStack_130,*puVar5);
              cVar7 = FUN_008f610c(auStack_12c,auStack_128);
              iVar11 = iVar10 + 1;
              if (cVar7 != '\0') {
                (*(code *)**(undefined4 **)(*piVar3 + 0xc))(piVar3,auStack_120,iVar10);
                FUN_008f5ecc(0,auStack_e0,auStack_f8);
                FUN_008f5e74((double)fStack_100,auStack_e0);
                FUN_008f5f60(auStack_e0,auStack_120,auStack_110);
                FUN_008f6054(auStack_12c,auStack_128,auStack_e0);
              }
              iVar10 = iVar11;
            } while (iVar4 != iVar11);
          }
        }
      }
      uVar8 = uVar8 + 1;
    } while (uVar8 != 0x10);
  }
  return;
}


////////////////////////////////////////////////////////////////
// 0018fd5c: no function (creating)
// ARSR_m7 @ 0018fd5c  size=1
// callers: 
// callees: 

void ARSR_m7(int param_1,undefined4 param_2,int *param_3)

{
  bool bVar1;
  int *piVar2;
  char cVar5;
  int iVar3;
  undefined4 *puVar4;
  int *piVar6;
  undefined1 auStack_5c [8];
  undefined1 auStack_54 [12];
  
  if (param_3 != (int *)0x0) {
    cVar5 = (*(code *)**(undefined4 **)(*param_3 + 8))(param_3);
    if (cVar5 == '\0') {
      return;
    }
    cVar5 = (*(code *)**(undefined4 **)(*param_3 + 0x88))(param_3);
    if ((cVar5 != '\0') &&
       (cVar5 = (*(code *)**(undefined4 **)(*param_3 + 0x8c))(param_3), cVar5 != '\0')) {
      iVar3 = (*(code *)**(undefined4 **)(*param_3 + 0x3c))(param_3);
      if (iVar3 == 0) {
        (*(code *)**(undefined4 **)(*param_3 + 0x40))(param_3);
      }
      piVar6 = (int *)(param_1 + 8);
      iVar3 = *piVar6;
      if (iVar3 == 0) {
        func_0x0018e320(param_1 + 0x19c);
        func_0x0018e320(param_1 + 0x1b0);
        iVar3 = FUN_00bc1974(0x394f0);
        func_0x0018f3b8(iVar3);
        if (iVar3 == 0) {
          iVar3 = *piVar6;
        }
        else {
          func_0x0018ead4(iVar3,param_1 + 0x50);
          *(int *)(&LAB_00039138 + iVar3) = param_1 + 0x1b0;
          *(int *)(&DAT_00039134 + iVar3) = param_1 + 0x19c;
          puVar4 = (undefined4 *)FUN_00bc1974(0x10);
          *puVar4 = &PTR_PTR_LAB_016be268;
          puVar4[1] = 1;
          *puVar4 = &PTR_PTR_LAB_016c69f8;
          puVar4[2] = 1;
          puVar4[3] = iVar3;
          *piVar6 = iVar3;
          *(undefined4 **)(param_1 + 0xc) = puVar4;
          FUN_00a8af48(auStack_54);
          iVar3 = *piVar6;
        }
      }
      func_0x0018e7d8(iVar3,param_2,param_3);
      FUN_001a391c(*piVar6 + 0x3914c,*(undefined4 *)(param_1 + 0x44));
      func_0x001a3e88(*piVar6 + 0x3914c,0,*(undefined4 *)(param_1 + 0x48));
      func_0x001a3e64(*piVar6 + 0x3914c,0,*(undefined4 *)(param_1 + 0x4c));
      piVar6 = *(int **)(param_1 + 0x40);
      bVar1 = piVar6 == (int *)0x0;
      if (bVar1) {
        return;
      }
      if (*(char *)(param_1 + 0x1ac) == '\0') {
        cVar5 = (*(code *)**(undefined4 **)(*piVar6 + 8))(piVar6,param_1 + 0x19c);
        if (cVar5 == '\0') {
          piVar6 = *(int **)(param_1 + 0x40);
          bVar1 = piVar6 == (int *)0x0;
        }
        else {
          piVar6 = *(int **)(param_1 + 0x40);
          bVar1 = piVar6 == (int *)0x0;
          *(undefined1 *)(param_1 + 0x1ac) = 1;
        }
      }
      if (bVar1) {
        return;
      }
      if (*(char *)(param_1 + 0x1c0) != '\0') {
        return;
      }
      cVar5 = (*(code *)**(undefined4 **)(*piVar6 + 8))(piVar6,param_1 + 0x1b0);
      if (cVar5 == '\0') {
        return;
      }
      *(undefined1 *)(param_1 + 0x1c0) = 1;
      return;
    }
  }
  piVar6 = (int *)(param_1 + 8);
  if (*piVar6 != 0) {
    piVar2 = *(int **)(param_1 + 0x40);
    if (piVar2 != (int *)0x0) {
      (*(code *)**(undefined4 **)(*piVar2 + 0x14))(piVar2,param_1 + 0x19c);
      *(undefined1 *)(param_1 + 0x1ac) = 0;
      (*(code *)**(undefined4 **)(**(int **)(param_1 + 0x40) + 0x14))
                (*(int **)(param_1 + 0x40),param_1 + 0x1b0);
      *(undefined1 *)(param_1 + 0x1c0) = 0;
    }
    FUN_00abbf28(param_1 + 0x10);
    FUN_0018e974(*piVar6);
    *piVar6 = 0;
    *(undefined4 *)(param_1 + 0xc) = 0;
    FUN_00a8af48(auStack_5c);
    FUN_00abbde0(param_1 + 0x10);
  }
  return;
}


