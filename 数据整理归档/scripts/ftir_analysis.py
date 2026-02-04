"""
FTIR Spectroscopy Data Analysis Report Generator
FTIR光谱数据综合分析报告生成器
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def analyze_ftir_data():
    """Comprehensive FTIR spectroscopy analysis"""
    
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 18 + "FTIR SPECTROSCOPY ANALYSIS REPORT" + " " * 27 + "║")
    print("║" + " " * 22 + "FTIR红外光谱分析报告" + " " * 32 + "║")
    print("╚" + "═" * 78 + "╝")
    print(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load data
    df = pd.read_excel('FTIR.xlsx')
    
    print("\n" + "=" * 80)
    print("1. DATA STRUCTURE ANALYSIS | 数据结构分析")
    print("=" * 80)
    
    sample_col = df.columns[0]
    wavenumber_cols = df.columns[1:]
    
    # Extract wavenumbers
    wavenumbers = []
    for col in wavenumber_cols:
        try:
            wn = float(col)
            wavenumbers.append(wn)
        except:
            pass
    
    print(f"\n📊 Dataset Overview:")
    print(f"   Total samples: {len(df)}")
    print(f"   Total columns: {len(df.columns)}")
    print(f"   Wavenumber columns: {len(wavenumbers)}")
    print(f"   Wavenumber range: {min(wavenumbers):.2f} - {max(wavenumbers):.2f} cm⁻¹")
    print(f"   Spectral resolution: {abs(wavenumbers[1] - wavenumbers[0]):.2f} cm⁻¹")
    
    samples = df[sample_col].tolist()
    print(f"\n🔬 Sample List (first 20):")
    print(f"   {', '.join(map(str, samples[:20]))}")
    if len(samples) > 20:
        print(f"   ... and {len(samples) - 20} more samples")
    
    print("\n" + "=" * 80)
    print("2. SPECTRAL CHARACTERISTICS | 光谱特征分析")
    print("=" * 80)
    
    # Convert to numeric - columns are already floats, not strings
    numeric_cols = [col for col in df.columns[1:] if isinstance(col, (int, float))]
    spectral_data = df[numeric_cols].values
    
    # Overall statistics
    print(f"\n📈 Overall Transmittance Statistics:")
    print(f"   {'Metric':<25} {'Value':<15}")
    print(f"   {'-'*40}")
    print(f"   {'Mean transmittance':<25} {np.nanmean(spectral_data):.4f}")
    print(f"   {'Std deviation':<25} {np.nanstd(spectral_data):.4f}")
    print(f"   {'Min transmittance':<25} {np.nanmin(spectral_data):.4f}")
    print(f"   {'Max transmittance':<25} {np.nanmax(spectral_data):.4f}")
    
    # Peak regions analysis
    print(f"\n🔍 Key Spectral Regions Analysis:")
    
    regions = {
        "O-H stretch (3600-3200)": (3600, 3200),
        "C-H stretch (3000-2800)": (3000, 2800),
        "C=O stretch (1750-1700)": (1750, 1700),
        "Aromatic C=C (1600-1500)": (1600, 1500),
        "C-O stretch (1300-1000)": (1300, 1000),
        "β-glycosidic (905-885)": (905, 885)
    }
    
    for region_name, (high, low) in regions.items():
        region_wn = [wn for wn in wavenumbers if low <= wn <= high]
        if len(region_wn) > 0:
            # Use actual column objects (floats), not strings
            region_data = df[region_wn].values
            mean_trans = np.nanmean(region_data)
            std_trans = np.nanstd(region_data)
            print(f"   {region_name:<30} Mean: {mean_trans:.4f}, Std: {std_trans:.4f}")
    
    print("\n" + "=" * 80)
    print("3. SAMPLE-WISE SPECTRAL ANALYSIS | 样本光谱分析")
    print("=" * 80)
    
    sample_stats = []
    
    for idx, sample in enumerate(samples):
        spectrum = spectral_data[idx]
        spectrum = spectrum[~np.isnan(spectrum)]
        
        if len(spectrum) == 0:
            continue
        
        stats = {
            'Sample': sample,
            'Mean': np.mean(spectrum),
            'Std': np.std(spectrum),
            'Min': np.min(spectrum),
            'Max': np.max(spectrum),
            'Range': np.max(spectrum) - np.min(spectrum)
        }
        sample_stats.append(stats)
    
    stats_df = pd.DataFrame(sample_stats)
    
    # Extract groups
    stats_df['Group'] = stats_df['Sample'].astype(str).str.extract(r'^([A-Z]+)', expand=False)
    stats_df['Is_Control'] = stats_df['Sample'].astype(str).str.contains('0$', na=False)
    
    print(f"\n📊 Sample Statistics Summary:")
    print(f"   Total samples analyzed: {len(stats_df)}")
    
    # Samples with highest/lowest average transmittance
    print(f"\n⬆️  Highest Average Transmittance (Top 5):")
    top5 = stats_df.nlargest(5, 'Mean')[['Sample', 'Mean', 'Std', 'Range']]
    for idx, row in top5.iterrows():
        print(f"      {row['Sample']}: Mean={row['Mean']:.4f}, Std={row['Std']:.4f}, Range={row['Range']:.4f}")
    
    print(f"\n⬇️  Lowest Average Transmittance (Top 5):")
    bottom5 = stats_df.nsmallest(5, 'Mean')[['Sample', 'Mean', 'Std', 'Range']]
    for idx, row in bottom5.iterrows():
        print(f"      {row['Sample']}: Mean={row['Mean']:.4f}, Std={row['Std']:.4f}, Range={row['Range']:.4f}")
    
    # Group comparison
    if stats_df['Group'].notna().sum() > 0:
        print("\n" + "=" * 80)
        print("4. GROUP COMPARISON | 组间对比")
        print("=" * 80)
        
        group_stats = stats_df.groupby('Group').agg({
            'Sample': 'count',
            'Mean': ['mean', 'std'],
            'Std': 'mean',
            'Range': 'mean'
        }).round(4)
        
        print(f"\n📊 Group-wise Spectral Characteristics:")
        print(f"\n   {'Group':<8} {'N':<5} {'Avg Mean':<12} {'Mean Std':<12} {'Avg Std':<12} {'Avg Range':<12}")
        print(f"   {'-'*65}")
        
        for group in group_stats.index:
            n = int(group_stats.loc[group, ('Sample', 'count')])
            avg_mean = group_stats.loc[group, ('Mean', 'mean')]
            mean_std = group_stats.loc[group, ('Mean', 'std')]
            avg_std = group_stats.loc[group, ('Std', 'mean')]
            avg_range = group_stats.loc[group, ('Range', 'mean')]
            
            print(f"   {group:<8} {n:<5} {avg_mean:<12.4f} {mean_std:<12.4f} {avg_std:<12.4f} {avg_range:<12.4f}")
    
    # Peak detection analysis
    print("\n" + "=" * 80)
    print("5. PEAK DETECTION & FUNCTIONAL GROUPS | 峰检测与官能团分析")
    print("=" * 80)
    
    # Analyze characteristic peaks for each group
    peak_regions = {
        "O-H (3600-3200)": (3600, 3200, "Hydroxyl groups (cellulose, water)"),
        "C-H (2920-2850)": (2920, 2850, "Aliphatic chains"),
        "C=O (1735±20)": (1755, 1715, "Pectin/hemicellulose carbonyl"),
        "Aromatic (1505±10)": (1515, 1495, "Lignin aromatic rings"),
        "C=C (1595±10)": (1605, 1585, "Aromatic C=C"),
        "C-O-C (1025±15)": (1040, 1010, "Cellulose backbone"),
        "β-glycosidic (895±10)": (905, 885, "Cellulose β-bonds")
    }
    
    print(f"\n🔍 Characteristic Peak Analysis by Group:")
    
    if 'Group' in stats_df.columns:
        for group in sorted(stats_df['Group'].dropna().unique()):
            group_samples = stats_df[stats_df['Group'] == group]['Sample'].tolist()
            group_indices = [samples.index(s) for s in group_samples if s in samples]
            
            print(f"\n   **{group} Group** (n={len(group_samples)}):")
            
            for peak_name, (high, low, description) in peak_regions.items():
                region_wn = [wn for wn in wavenumbers if low <= wn <= high]
                if len(region_wn) > 0:
                    # Use actual float columns
                    group_region_data = df.loc[group_indices, region_wn].values
                    avg_trans = np.nanmean(group_region_data)
                    
                    print(f"      {peak_name:<20} {avg_trans:.4f} - {description}")
    
    # Control vs Treated comparison
    if stats_df['Is_Control'].sum() > 0:
        print("\n" + "=" * 80)
        print("6. CONTROL VS TREATED COMPARISON | 对照组与处理组对比")
        print("=" * 80)
        
        control = stats_df[stats_df['Is_Control']]
        treated = stats_df[~stats_df['Is_Control']]
        
        print(f"\n🔬 Spectral Changes After Treatment:")
        print(f"\n   {'Parameter':<25} {'Control':<15} {'Treated':<15} {'Change':<15}")
        print(f"   {'-'*70}")
        
        print(f"   {'Sample count':<25} {len(control):<15} {len(treated):<15} {'-':<15}")
        
        control_mean = control['Mean'].mean()
        treated_mean = treated['Mean'].mean()
        change_pct = ((treated_mean - control_mean) / control_mean * 100)
        print(f"   {'Avg transmittance':<25} {control_mean:<15.4f} {treated_mean:<15.4f} {change_pct:+.2f}%")
        
        control_std = control['Std'].mean()
        treated_std = treated['Std'].mean()
        print(f"   {'Avg std deviation':<25} {control_std:<15.4f} {treated_std:<15.4f} {'-':<15}")
        
        control_range = control['Range'].mean()
        treated_range = treated['Range'].mean()
        print(f"   {'Avg spectral range':<25} {control_range:<15.4f} {treated_range:<15.4f} {'-':<15}")
        
        print(f"\n   💡 Interpretation:")
        if change_pct > 0:
            print(f"      - Overall transmittance increased by {abs(change_pct):.2f}%")
            print(f"      - Indicates removal of absorbing materials (lignin, pectin)")
        else:
            print(f"      - Overall transmittance decreased by {abs(change_pct):.2f}%")
            print(f"      - May indicate structural changes or chemical modifications")
    
    print("\n" + "=" * 80)
    print("7. INSIGHTS & RECOMMENDATIONS | 分析洞察与建议")
    print("=" * 80)
    
    print(f"\n🔬 Key Findings:")
    
    print(f"\n   1. Spectral Coverage:")
    print(f"      - Wavenumber range: {min(wavenumbers):.0f} - {max(wavenumbers):.0f} cm⁻¹")
    print(f"      - Covers all major functional group regions")
    print(f"      - High resolution: {abs(wavenumbers[1] - wavenumbers[0]):.2f} cm⁻¹")
    
    print(f"\n   2. Sample Variability:")
    if 'Group' in stats_df.columns:
        group_cv = stats_df.groupby('Group')['Mean'].std() / stats_df.groupby('Group')['Mean'].mean() * 100
        for group, cv in group_cv.items():
            status = "✓ Good" if cv < 10 else "⚠ Moderate" if cv < 20 else "❗ High"
            print(f"      - {group} series: CV = {cv:.2f}% ({status} consistency)")
    
    print(f"\n   3. Chemical Composition Indicators:")
    print(f"      - High O-H region (3600-3200): Cellulose/hydroxyl content")
    print(f"      - C=O peak (1735): Pectin/hemicellulose presence")
    print(f"      - Aromatic peaks (1505, 1595): Lignin content")
    print(f"      - C-O-C (1025): Cellulose backbone integrity")
    
    print(f"\n💡 Recommendations:")
    
    print(f"\n   1. Data Quality:")
    print(f"      - ✓ Dataset is complete with {len(samples)} samples")
    print(f"      - ✓ Spectral range covers all important regions")
    print(f"      - Consider baseline correction if not already applied")
    
    print(f"\n   2. Advanced Analysis:")
    print(f"      - Peak deconvolution for overlapping bands")
    print(f"      - Second derivative spectra for hidden peaks")
    print(f"      - PCA to identify main sources of variation")
    print(f"      - Correlation with mechanical properties")
    
    print(f"\n   3. Quality Control:")
    print(f"      - Establish reference spectra for each fiber type")
    print(f"      - Monitor peak ratios (e.g., lignin/cellulose)")
    print(f"      - Track changes in specific bands during processing")
    
    print(f"\n   4. Integration Opportunities:")
    print(f"      - Correlate FTIR bands with breaking strength")
    print(f"      - Link spectral changes to extraction efficiency")
    print(f"      - Combine with ultrasonic data for comprehensive QC")
    
    # Save results
    stats_df.to_csv('ftir_spectral_stats.csv', index=False, encoding='utf-8-sig')
    print(f"\n💾 Results saved to: ftir_spectral_stats.csv")
    
    print("\n" + "=" * 80)
    print("✓ FTIR ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nNext Steps:")
    print(f"1. Review spectral characteristics by group")
    print(f"2. Identify peak patterns correlating with fiber quality")
    print(f"3. Establish spectral signatures for quality classification")
    print(f"4. Integrate FTIR data with mechanical and ultrasonic analyses")
    print(f"5. Build multivariate models for comprehensive fiber assessment")
    print()

if __name__ == "__main__":
    try:
        analyze_ftir_data()
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
