#!/usr/bin/env python3
"""
update_singular_symmetries.py - Cleanly update SingularSymmetries.tex by excising the Catalan diversion
and moving the Polyrhythmic Percussion Suite to the Appendix.

Author: Gemma Knee
"""

import os

def update_file():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sec", "SingularSymmetries.tex"))
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find where the stabiliser spectrum list ends
    split_target = "\\end{itemize}"
    # The last \\end{itemize} before \\subsection{The 295 Dimers
    dimer_idx = content.find("\\subsection{The 295 Dimers (2-Cycles)}")
    if dimer_idx == -1:
        raise ValueError("Could not find Dimers subsection")

    # Find the end of the monomer size list before dimer_idx
    # Let's locate \item \textbf{Order 1 ($|O| = 32$, 6 monomers)}:
    order1_idx = content.find("Order 1 ($|O| = 32$, 6 monomers)")
    end_list_idx = content.find("\\end{itemize}", order1_idx)
    if end_list_idx == -1 or end_list_idx > dimer_idx:
        raise ValueError("Could not locate \\end{itemize} after Order 1")

    end_list_idx += len("\\end{itemize}")

    dimers_text = content[dimer_idx:]

    new_content = content[:end_list_idx] + "\n\n" + dimers_text

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("✓ Successfully updated SingularSymmetries.tex")

if __name__ == "__main__":
    update_file()
