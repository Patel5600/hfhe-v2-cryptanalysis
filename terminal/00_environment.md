# Terminal Session 00 — Environment Setup

## Host

    OS:     Windows 11 (10.0.26200)
    Shell:  PowerShell 7
    Python: 3.14.2 [MSC v.1944 64 bit (AMD64)]
    Git:    2.53.0.windows.2

## Python packages

    numpy==2.4.1
    scipy==1.17.0
    pycryptodome==3.23.0
    matplotlib==3.10.x (installed during investigation)

## Repository clones

    git clone https://github.com/octra-labs/hfhe-challenge  C:\Dev\octra
    git clone https://github.com/octra-labs/pvac_hfhe_cpp   C:\Dev\pvac_hfhe_cpp

## Source pin

    cd C:\Dev\pvac_hfhe_cpp
    git log -1 --format="%H %ai %s"
    # 071b0e909c119de815e284b347c4bd979cb59ef3 2026-07-09 18:29:59 +0000 public matrix sampling
