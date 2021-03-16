from digital_manuscript import BnF

manuscript = BnF(apply_corrections = False)

for identity, entry in manuscript.entries.items():
    print(identity)
