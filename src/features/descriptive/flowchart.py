from pathlib import Path
import pandas as pd
from data.util.constants import SCANS_PROCESSED


def make_chart(data: pd.DataFrame, out_path: Path):
    data_spiro = data[data.GOLD_stage == '0']
    data_resp = data_spiro[(data_spiro.copd_diagnosis == False)
                       & (data_spiro.asthma_diagnosis == False)
                       & (data_spiro.cancer_type != "LONGKANKER")
                       & (data_spiro.cancer_type != "BORST LONG")]

    counts = {
        "Processed": SCANS_PROCESSED,
        "Poor Segmentations": SCANS_PROCESSED - len(data),
        "Abnormal Spirometry": (len(data) - len(data_spiro)),
        "Respiratory Disease": (len(data_spiro) - len(data_resp)),
        "Healthy": len(data_resp),
        "Healthy Never-Smokers": len(data_resp[data_resp.never_smoker == True]),
        "Healthy Ex-Smokers": len(data_resp[data_resp.ex_smoker == True]),
        "Healthy Current-Smokers": len(data_resp[data_resp.current_smoker == True]),
        "Healthy No-Status": len(data["smoking_status"].isnull())
    }

    counts["Healthy No-Status"] = counts["Healthy"] - sum(
        list(counts.values())[5:8])
    head = ",".join(counts.keys())
    vals = ",".join([str(num) for num in counts.values()])
    with open((out_path / "participant_flowchart.csv"), "w") as f:
        f.write(f"{head}\n")
        f.write(vals)

    mermaid = f"flowchart TD\nA[fa:fa-users All Participants - {counts['Processed']}] -->|fa:fa-lungs Normal Spirometry\\nfa:fa-head-side-cough No Respiratory Disease\\nfa:fa-lungs-virus No Hx Lung Cancer\\nfa:fa-prescription-bottle-medical No Rx use for Resp Disease| B(fa:fa-heart-pulse Healthy General Population - {counts['Healthy']})\nB --> C[fa:fa-user Never-Smokers\\n{counts['Healthy Never-Smokers']}]\nB --> D[fa:fa-ban-smoking Ex-Smokers\\n{counts['Healthy Ex-Smokers']}]\nB --> E[fa:fa-smoking Current-Smokers\\n{counts['Healthy Current-Smokers']}]\nB -.-> F[No Smoking Hx\\n{counts['Healthy No-Status']}]"

    with open((out_path / "participant_flowchart.md"), "w") as f:
        f.write(mermaid)
