def end_concrete_printing() -> str:
    end_conc_printing = (
        f"\n"
        f"\n;FOLD    3DCP"
        f"\n  RET = RSI_OFF() "
        f"\n  IF (RET <> RSIOK) THEN "
        f"\n    HALT "
        f"\n  ENDIF "
        f"\n  $ENERGY_MEASURING.ACTIVE = FALSE"
        f"\n"
        f"\n  $TIMER_STOP[1] = TRUE"
        f"\n  $TIMER_STOP[4] = TRUE"
        f"\n;ENDFOLD 3DCP"
        f"\n"
        f"\nEND"
    )
    return end_conc_printing
