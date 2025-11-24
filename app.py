import streamlit as st
from datetime import datetime
import io

# ===== QC LIMITS =====
QC_LIMITS = {
    "CT_no_accuracy": (-7, 7),
    "Intrinsic_Uniformity": (0, 3),
    "Extrinsic_Uniformity": (2, 4),
    "SUV_Accuracy": (-10, 10),
    "Sensitivity": (6, 12),
    "Dose Calibrator Constancy": (-5, 5),
    "Integral Uniformity": (0, 3),
    "Differential Uniformity": (0, 2),
    "Intrinsic Spatial Resolution": (3, 5),
    "COR Error": (-1, 1),
    "Spatial Resolution @ 1 cm": (3, 5),
    "Spatial Resolution @ 10 cm": (4, 6),
    "Sensitivity @ 0 cm": (7, 9),
    "Sensitivity @ 10 cm": (6, 8),
    "Scatter Fraction": (36, 40),
    "NECR Peak": (120, 140),
    "Image Quality – RC(22 mm sphere)": (0.85, 0.95),
    "Background Variability": (4, 6),
}

TEST_CATEGORY = {
    "CT_no_accuracy": "CT",
    "Intrinsic_Uniformity": "SPECT",
    "Extrinsic_Uniformity": "SPECT",
    "Integral Uniformity": "SPECT",
    "Differential Uniformity": "SPECT",
    "Intrinsic Spatial Resolution": "SPECT",
    "COR Error": "SPECT",
    "SUV_Accuracy": "PET",
    "Sensitivity": "PET",
    "Spatial Resolution @ 1 cm": "PET",
    "Spatial Resolution @ 10 cm": "PET",
    "Sensitivity @ 0 cm": "PET",
    "Sensitivity @ 10 cm": "PET",
    "Scatter Fraction": "PET",
    "NECR Peak": "PET",
    "Image Quality – RC(22 mm sphere)": "PET",
    "Background Variability": "PET",
    "Dose Calibrator Constancy": "Dose Calibrator",
}


def check_qc(measured: float, lower: float, upper: float) -> str:
    return "PASS" if lower <= measured <= upper else "FAIL"


def build_report(system_name: str, results: list) -> str:
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M")
    year_str = now.strftime("%Y")

    total_tests = len(results)
    n_pass = sum(1 for r in results if r["status"] == "PASS")
    n_fail = sum(1 for r in results if r["status"] == "FAIL")

    failed_tests = [r["test_name"] for r in results if r["status"] == "FAIL"]
    failed_list_text = ", ".join(failed_tests) if failed_tests else ""

    # Final judgment
    if n_fail == 0 and total_tests > 0:
        final_judgment = (
            "System Status: APPROVED for clinical use.\n"
            "All evaluated QC parameters are within the defined tolerance limits."
        )
    elif total_tests == 0:
        final_judgment = (
            "System Status: NOT EVALUATED.\n"
            "No QC measurements were entered in this session."
        )
    else:
        lines = ["System Status: NOT APPROVED for clinical use."]
        if failed_list_text:
            lines.append(
                f"The following QC parameters are outside the defined tolerance limits: {failed_list_text}."
            )
        lines.append(
            "Corrective action, service intervention, and repeat QC testing are required "
            "before returning the system to clinical operation."
        )
        final_judgment = "\n".join(lines)

    lines = []
    lines.append("KUWAIT CANCER CONTROL CENTER")
    lines.append("Nuclear Medicine Department – Physics Unit")
    lines.append(f"QC Report {year_str}")
    lines.append("")
    lines.append(f"System        : {system_name}")
    lines.append(f"Date & Time   : {date_str}")
    lines.append(f"Total Tests   : {total_tests}")
    lines.append(f"PASS / FAIL   : {n_pass} / {n_fail}")
    lines.append("=" * 60)
    lines.append("")

    # Group by category
    categories_order = ["SPECT", "PET", "Dose Calibrator", "CT", "Other"]
    cat_results = {cat: [] for cat in categories_order}
    for r in results:
        cat = TEST_CATEGORY.get(r["test_name"], "Other")
        if cat not in cat_results:
            cat_results[cat] = []
        cat_results[cat].append(r)

    header = f"{'Test Name':45} {'Measured':>10} {'Lower':>10} {'Upper':>10} {'Status':>8}"

    for cat in categories_order:
        tests_in_cat = cat_results.get(cat, [])
        if not tests_in_cat:
            continue

        lines.append(f"{cat} QC RESULTS")
        lines.append("-" * len(header))
        lines.append(header)
        lines.append("-" * len(header))

        for r in tests_in_cat:
            line = (
                f"{r['test_name'][:45]:45}"
                f" {r['measured']:10.3f}"
                f" {r['lower']:10.3f}"
                f" {r['upper']:10.3f}"
                f" {r['status']:>8}"
            )
            lines.append(line)

        lines.append("")

    lines.append("SUMMARY")
    lines.append("-" * 60)
    lines.append(f"Number of tests evaluated : {total_tests}")
    lines.append(f"Number of PASS            : {n_pass}")
    lines.append(f"Number of FAIL            : {n_fail}")
    lines.append("")
    lines.append("CONCLUSION")
    lines.append("-" * 60)
    lines.append(final_judgment)
    lines.append("")
    lines.append("-" * 60)
    lines.append("Prepared by:   Nuclear Medicine Physics Unit")
    lines.append("Approved by:   Head of Radiation Physics Department")
    lines.append("-" * 60)
    lines.append("")

    return "\n".join(lines)


# ===== STREAMLIT APP =====

def main():
    st.set_page_config(page_title="KCCC QC Report Portal", layout="wide")

    st.title("KCCC QC Report Portal")
    st.markdown("Nuclear Medicine Department – Physics Unit")

    with st.sidebar:
        st.header("System Information")
        system_name = st.text_input(
            "System name",
            value="GE Discovery MI Gen 2 PET/CT",
            help="Enter scanner or equipment name",
        )
        st.markdown("---")
        st.write("Instructions:")
        st.write("- Enter measured values for each test")
        st.write("- Leave blank if not performed")
        st.write("- Tick **NA** if test is not applicable")

    # Prepare data entry structure
    st.subheader("QC Data Entry")

    categories_order = ["SPECT", "PET", "Dose Calibrator", "CT", "Other"]
    cat_tests = {cat: [] for cat in categories_order}
    for test_name, (lower, upper) in QC_LIMITS.items():
        cat = TEST_CATEGORY.get(test_name, "Other")
        if cat not in cat_tests:
            cat_tests[cat] = []
        cat_tests[cat].append((test_name, lower, upper))

    measured_results = []

    # Show separate sections
    for cat in categories_order:
        tests = cat_tests.get(cat, [])
        if not tests:
            continue

        with st.expander(f"{cat} QC Tests", expanded=True):
            for test_name, lower, upper in tests:
                cols = st.columns([3, 2, 2, 2, 1])
                with cols[0]:
                    st.markdown(f"**{test_name}**")
                with cols[1]:
                    st.write(f"Limits: {lower} to {upper}")
                with cols[2]:
                    value = st.text_input(
                        "Measured",
                        key=f"val_{test_name}",
                        placeholder="e.g. 4.5",
                    )
                with cols[3]:
                    na = st.checkbox("NA", key=f"na_{test_name}")
                with cols[4]:
                    st.write("")  # spacing

                if na:
                    # Not applicable: ignore this test
                    continue

                if value.strip() == "":
                    # Not entered
                    continue

                try:
                    measured = float(value)
                except ValueError:
                    st.warning(f"{test_name}: invalid number, ignored.")
                    continue

                status = check_qc(measured, lower, upper)
                measured_results.append(
                    {
                        "category": cat,
                        "test_name": test_name,
                        "measured": measured,
                        "lower": lower,
                        "upper": upper,
                        "status": status,
                    }
                )

    st.markdown("---")
    if st.button("Generate QC Report"):
        if not measured_results:
            st.error("No valid QC measurements entered.")
            return

        # Show results dashboard
        st.subheader("QC Results Overview")

        # Show summary by category
        for cat in categories_order:
            cat_res = [r for r in measured_results if r["category"] == cat]
            if not cat_res:
                continue
            st.markdown(f"### {cat} Results")
            rows = []
            for r in cat_res:
                rows.append(
                    {
                        "Test Name": r["test_name"],
                        "Measured": r["measured"],
                        "Lower": r["lower"],
                        "Upper": r["upper"],
                        "Status": r["status"],
                    }
                )
            st.table(rows)

        # Build report text
        report_text = build_report(system_name, measured_results)

        # Show summary counts and conclusion
        n_pass = sum(1 for r in measured_results if r["status"] == "PASS")
        n_fail = sum(1 for r in measured_results if r["status"] == "FAIL")
        st.markdown("### Summary")
        st.write(f"Total tests evaluated: {len(measured_results)}")
        st.write(f"PASS: {n_pass}")
        st.write(f"FAIL: {n_fail}")

        st.markdown("### Generated Report (Preview)")
        st.text(report_text)

        # Prepare downloadable file
        buffer = io.BytesIO()
        buffer.write(report_text.encode("utf-8"))
        buffer.seek(0)

        filename = f"QC_Report_{system_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"

        st.download_button(
            label="Download QC Report (.txt)",
            data=buffer,
            file_name=filename,
            mime="text/plain",
        )


if __name__ == "__main__":
    main()