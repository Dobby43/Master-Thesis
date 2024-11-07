def project_setup(file: [str]) -> str:
    filename = file.upper()
    setup = (
        f"DEF {filename} ( )"
        f"\n"
        f"\n;Declarations for RSI "
        f"\nDECL INT RET "
        f"\nDECL INT CONTID "
        f"\n"
    )
    return setup


def initialisation() -> str:
    initialisation = (
        f"\n;FOLD       INI"
        f"\n  ;FOLD     BASISTECH INI"
        f"\n    GLOBAL INTERRUPT DECL 3 WHEN $STOPMESS==TRUE DO IR_STOPM ( )"
        f"\n    INTERRUPT ON 3"
        f"\n    BAS (#INITMOV,0)"
        f"\n   ;ENDFOLD BASISTECH INI"
        f"\n;ENDFOLD    INI"
        f"\n"
    )
    return initialisation


def start_concrete_printing():
    start_conc_printing = (
        f"\n;FOLD    3DCP"
        f'\n  RET = RSI_CREATE("rsi3dcp",CONTID,TRUE)'
        f"\n  IF (RET <> RSIOK) THEN"
        f"\n    HALT"
        f"\n  ENDIF"
        f"\n"
        f"\n  RET = RSI_ON(#ABSOLUTE)"
        f"\n  IF (RET <> RSIOK) THEN"
        f"\n    HALT"
        f"\n  ENDIF"
        f"\n"
        f"\n ; IF $USER_LEVEL > 19 THEN  ;EXPERT Mode required"
        f'\n ;   MyHmiOpen("dn",#Half)'
        f"\n ; ENDIF"
        f"\n"
        f"\n  PRINT_PROGRESS = 0"
        f"\n  LAYER = 1"
        f"\n"
        f"\n  $TIMER[1] = 0 ;Reset"
        f"\n  $TIMER_STOP[1] = FALSE ;Start"
        f"\n"
        f"\n  $TIMER[4] = 0 ;Reset"
        f"\n  $TIMER_STOP[4] = FALSE ;Start"
        f"\n"
        f"\n  IF $ENERGY_MEASURING.ACTIVE == TRUE THEN"
        f"\n    $ENERGY_MEASURING.ACTIVE = FALSE"
        f"\n    $ENERGY_MEASURING.ACTIVE = TRUE"
        f"\n  ELSE"
        f"\n    $ENERGY_MEASURING.ACTIVE = TRUE"
        f"\n  ENDIF"
        f"\n;ENDFOLD 3DCP"
        f"\n"
    )
    return start_conc_printing


def block_coordinates(
    base: str, tool: str, t_1: str, t_2: str, aut: str, default: str, start_pos: str
) -> [str]:

    block_coordinates = (
        f"\n;FOLD    BCO"
        f"\n  TOOL_DATA[1] = {tool}"
        f"\n  BASE_DATA[1] = {base}"
        f"\n  $BWDSTART = FALSE"
        f"\n"
        f"\n  SWITCH $MODE_OP"
        f"\n    CASE #T1"
        f"\n      PDAT_ACT =  {t_1}"
        f"\n      BAS (#PTP_PARAMS,100)"
        f"\n    CASE #T2"
        f"\n      PDAT_ACT = {t_2}"
        f"\n      BAS (#PTP_PARAMS,20)"
        f"\n    CASE #AUT"
        f"\n      PDAT_ACT = {aut}"
        f"\n      BAS (#PTP_PARAMS,20)"
        f"\n    DEFAULT"
        f"\n      PDAT_ACT = {default}"
        f"\n      BAS (#PTP_PARAMS,20)"
        f"\n   ENDSWITCH"
        f"\n"
        f"\n   FDAT_ACT = {{TOOL_NO 1,BASE_NO 1,IPO_FRAME #BASE}}"
        f"\n"
        f"\n   PTP  {start_pos}"
        f"\n;ENDFOLD BCO"
        f"\n"
    )

    a = f"""
    dsfsdf{start_pos}
    sdfsdf
    sdfsdf
    """
    return block_coordinates


def motion(vel_cp: float, vel_ori1: float, vel_ori2: float, adv: int) -> [str]:

    motion = (
        f"\n;FOLD    MOTION"
        f"\n   $VEL.CP   = {vel_cp:.0f} ;m/sec"
        f"\n   $VEL.ORI1 = {vel_ori1:.0f} ;deg/sec"
        f"\n   $VEL.ORI2 = {vel_ori2:.0f} ;deg/sec"
        f"\n   $ADVANCE = {adv:.0f}"
        f"\n;ENDFOLD MOTION"
        f"\n"
    )
    return motion
