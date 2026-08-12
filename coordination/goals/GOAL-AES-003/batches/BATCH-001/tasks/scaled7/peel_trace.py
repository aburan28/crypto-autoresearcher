"""How many ciphertext cells and last-round-key cells must be guessed to compute
ONE cell of the state n rounds back from the ciphertext, in MINI-AES-64.
Backward propagation of the dependency support only -- no key, no data."""
import json
def col(i): return i//4
def row(i): return i%4
def isr(i):   # inverse ShiftRows: cell (r,c) of the pre-SR state feeds (r,(c-r)%4)... source of (r,c) is (r,(c+r)%4)
    r,c=row(i),col(i); return 4*((c+r)%4)+r
def back(cells, last):
    """one round backwards; `last` = this was the final round (no MixColumns)"""
    out=set()
    for i in cells:
        j=isr(i)                       # through ISB (cellwise) and ISR
        if last: out.add(j)            # no MixColumns in the final round
        else: out.update(4*col(j)+r for r in range(4))   # IMC pulls the whole column
    return out
res={}
for nrounds in (1,2,3):
    cells={0}
    for k in range(nrounds):
        cells=back(cells, last=(k==nrounds-1))
    res[nrounds]={"ciphertext_cells_needed":len(cells),
                  "last_round_key_cells_guessed":len(cells),
                  "guess_space_bits_last_round_key":4*len(cells),
                  "plus_inner_round_key_cells":(0 if nrounds==1 else (1 if nrounds==2 else 4+1)),
                  "cells":sorted(cells)}
res["note"]=("2-round peel: 4 cells of K_R (2^16) + 1 cell of K'_{R-1} (2^4) = 2^20 per (diagonal,row). "
             "3-round peel: all 16 cells of K_R = 2^64, which IS the whole MINI-AES-64 key space.")
print(json.dumps(res,indent=1))
