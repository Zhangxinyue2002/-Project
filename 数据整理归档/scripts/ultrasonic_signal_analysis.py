"""
Ultrasonic Signal Analysis Report Generator
超声波信号分析报告生成器
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def analyze_ultrasonic_signals():
    """Comprehensive analysis of ultrasonic echo signals from fiber samples"""
    
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "ULTRASONIC SIGNAL ANALYSIS REPORT" + " " * 30 + "║")
    print("║" + " " * 20 + "超声波回波信号分析报告" + " " * 34 + "║")
    print("╚" + "═" * 78 + "╝")
    print(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load data
    df = pd.read_excel('数据集/Ultrasonic_signal.xlsx')
    
    print("\n" + "=" * 80)
    print("1. DATA OVERVIEW | 数据概览")
    print("=" * 80)
    
    # The data structure: First row contains sample names, subsequent rows contain signal values
    # Each column represents one sample's time-series signal
    
    sample_row = df.iloc[0]
    valid_samples = []
    sample_col_map = {}
    
    for col_idx, col in enumerate(df.columns):
        val = sample_row[col]
        if isinstance(val, str) and len(val) < 20 and not val.startswith('纤维'):
            valid_samples.append(val)
            sample_col_map[val] = col
    
    print(f"\n📊 Dataset Structure:")
    print(f"   Total rows (time points per sample): {len(df) - 1}")
    print(f"   Total columns: {len(df.columns)}")
    print(f"   Data format: Each column = one sample's signal time series")
    
    print(f"\n🔬 Detected Samples:")
    print(f"   Total unique sample IDs: {len(valid_samples)}")
    print(f"   Sample names: {', '.join(map(str, valid_samples[:20]))}")
    if len(valid_samples) > 20:
        print(f"   ... and {len(valid_samples) - 20} more samples")
    
    print(f"\n📡 Signal Characteristics:")
    print(f"   Signal type: Ultrasonic echo from fiber reflection")
    print(f"   Processing: Filtered, denoised, SNR enhanced")
    print(f"   Signal components:")
    print(f"      1. Direct bounce wave (发射波直接回弹)")
    print(f"      2. Fiber reflection wave (纤维反射波)")
    print(f"      3. Solution reflection wave (溶液反射波)")
    print(f"      4. Impurity bounce + noise (杂质回弹 + 噪声)")
    
    print("\n" + "=" * 80)
    print("2. SIGNAL STATISTICS ANALYSIS | 信号统计分析")
    print("=" * 80)
    
    # Collect all numeric signal data
    all_signal_data = []
    for sample in valid_samples:
        col = sample_col_map[sample]
        signal_vals = df[col].iloc[1:].values  # Skip first row (sample name)
        signal_vals = pd.to_numeric(signal_vals, errors='coerce')
        signal_vals = signal_vals[~np.isnan(signal_vals)]
        all_signal_data.extend(signal_vals.tolist())
    
    signal_data = np.array(all_signal_data)
    
    print(f"\n📈 Overall Signal Statistics:")
    print(f"   {'Metric':<25} {'Value':<20}")
    print(f"   {'-'*45}")
    print(f"   {'Mean amplitude':<25} {np.mean(signal_data):.6f}")
    print(f"   {'Std deviation':<25} {np.std(signal_data):.6f}")
    print(f"   {'Min amplitude':<25} {np.min(signal_data):.6f}")
    print(f"   {'Max amplitude':<25} {np.max(signal_data):.6f}")
    print(f"   {'Peak-to-peak':<25} {np.max(signal_data) - np.min(signal_data):.6f}")
    print(f"   {'RMS (Root Mean Square)':<25} {np.sqrt(np.mean(signal_data**2)):.6f}")
    
    # Signal energy analysis
    signal_energy = np.sum(signal_data**2)
    signal_power = signal_energy / len(signal_data)
    
    print(f"\n⚡ Signal Energy Analysis:")
    print(f"   Total energy: {signal_energy:.2e}")
    print(f"   Average power: {signal_power:.6f}")
    
    # Amplitude distribution
    print(f"\n📊 Amplitude Distribution:")
    percentiles = [1, 5, 25, 50, 75, 95, 99]
    for p in percentiles:
        val = np.percentile(signal_data, p)
        print(f"   {p:2d}th percentile: {val:8.4f}")
    
    print("\n" + "=" * 80)
    print("3. SAMPLE-WISE ANALYSIS | 逐样本分析")
    print("=" * 80)
    
    # Analyze each sample
    sample_stats = []
    
    for sample in valid_samples:
        col = sample_col_map[sample]
        
        # Get signal values for this sample (skip first row which is sample name)
        signal_vals = df[col].iloc[1:].values
        signal_vals = pd.to_numeric(signal_vals, errors='coerce')
        signal_vals = signal_vals[~np.isnan(signal_vals)]
        
        if len(signal_vals) == 0:
            continue
        
        stats = {
            'Sample': sample,
            'Points': len(signal_vals),
            'Mean': np.mean(signal_vals),
            'Std': np.std(signal_vals),
            'Min': np.min(signal_vals),
            'Max': np.max(signal_vals),
            'RMS': np.sqrt(np.mean(signal_vals**2)),
            'Peak2Peak': np.max(signal_vals) - np.min(signal_vals),
            'Energy': np.sum(signal_vals**2)
        }
        sample_stats.append(stats)
    
    stats_df = pd.DataFrame(sample_stats)
    
    print(f"\n📋 Sample Statistics Summary:")
    print(f"   Total samples analyzed: {len(stats_df)}")
    
    # Display top samples by different metrics
    print(f"\n🔊 Samples with Highest RMS (Signal Strength):")
    top_rms = stats_df.nlargest(5, 'RMS')[['Sample', 'RMS', 'Mean', 'Std']]
    for idx, row in top_rms.iterrows():
        print(f"      {row['Sample']}: RMS={row['RMS']:.4f}, Mean={row['Mean']:.4f}, Std={row['Std']:.4f}")
    
    print(f"\n📉 Samples with Lowest RMS (Weakest Signal):")
    bottom_rms = stats_df.nsmallest(5, 'RMS')[['Sample', 'RMS', 'Mean', 'Std']]
    for idx, row in bottom_rms.iterrows():
        print(f"      {row['Sample']}: RMS={row['RMS']:.4f}, Mean={row['Mean']:.4f}, Std={row['Std']:.4f}")
    
    print(f"\n⚡ Samples with Highest Energy:")
    top_energy = stats_df.nlargest(5, 'Energy')[['Sample', 'Energy', 'Peak2Peak']]
    for idx, row in top_energy.iterrows():
        print(f"      {row['Sample']}: Energy={row['Energy']:.2e}, P2P={row['Peak2Peak']:.4f}")
    
    print(f"\n📊 Samples with Largest Peak-to-Peak Variation:")
    top_p2p = stats_df.nlargest(5, 'Peak2Peak')[['Sample', 'Peak2Peak', 'Max', 'Min']]
    for idx, row in top_p2p.iterrows():
        print(f"      {row['Sample']}: P2P={row['Peak2Peak']:.4f} (Max={row['Max']:.4f}, Min={row['Min']:.4f})")
    
    # Group analysis (if sample naming follows pattern)
    stats_df['Group'] = stats_df['Sample'].str.extract(r'^([A-Z]+)', expand=False)
    
    if stats_df['Group'].notna().sum() > 0:
        print("\n" + "=" * 80)
        print("4. GROUP COMPARISON | 组间对比")
        print("=" * 80)
        
        group_stats = stats_df.groupby('Group').agg({
            'Sample': 'count',
            'RMS': ['mean', 'std'],
            'Mean': ['mean', 'std'],
            'Energy': 'mean',
            'Peak2Peak': 'mean'
        }).round(4)
        
        print(f"\n📊 Group-wise Signal Characteristics:")
        print(f"\n   {'Group':<8} {'N':<5} {'Avg RMS':<12} {'RMS Std':<12} {'Avg Mean':<12} {'Avg Energy':<15}")
        print(f"   {'-'*70}")
        
        for group in group_stats.index:
            n = int(group_stats.loc[group, ('Sample', 'count')])
            avg_rms = group_stats.loc[group, ('RMS', 'mean')]
            rms_std = group_stats.loc[group, ('RMS', 'std')]
            avg_mean = group_stats.loc[group, ('Mean', 'mean')]
            avg_energy = group_stats.loc[group, ('Energy', 'mean')]
            
            print(f"   {group:<8} {n:<5} {avg_rms:<12.4f} {rms_std:<12.4f} {avg_mean:<12.4f} {avg_energy:<15.2e}")
    
    print("\n" + "=" * 80)
    print("5. SIGNAL QUALITY ASSESSMENT | 信号质量评估")
    print("=" * 80)
    
    # Signal-to-Noise Ratio estimation
    # Assuming noise is related to the signal variation
    signal_mean = np.abs(np.mean(signal_data))
    noise_estimate = np.std(signal_data)
    snr_estimate = signal_mean / noise_estimate if noise_estimate > 0 else 0
    snr_db = 20 * np.log10(snr_estimate) if snr_estimate > 0 else -np.inf
    
    print(f"\n🔊 Signal Quality Metrics:")
    print(f"   Estimated SNR: {snr_estimate:.4f} ({snr_db:.2f} dB)")
    
    if snr_db > 20:
        quality = "Excellent"
    elif snr_db > 10:
        quality = "Good"
    elif snr_db > 5:
        quality = "Fair"
    else:
        quality = "Poor - needs noise reduction"
    
    print(f"   Signal quality: {quality}")
    
    # Consistency analysis
    cv = (np.std(signal_data) / np.abs(np.mean(signal_data))) * 100 if np.mean(signal_data) != 0 else 0
    print(f"   Coefficient of Variation: {cv:.2f}%")
    
    if cv < 10:
        consistency = "Very consistent signal"
    elif cv < 25:
        consistency = "Moderately consistent"
    else:
        consistency = "High variability - check for artifacts"
    
    print(f"   Signal consistency: {consistency}")
    
    print("\n" + "=" * 80)
    print("6. INSIGHTS & RECOMMENDATIONS | 分析洞察与建议")
    print("=" * 80)
    
    print(f"\n🔬 Key Findings:")
    
    # Finding 1: Signal characteristics
    print(f"\n   1. Signal Characteristics:")
    print(f"      - Overall amplitude range: {np.min(signal_data):.4f} to {np.max(signal_data):.4f}")
    print(f"      - Predominantly negative amplitudes indicate reflection/absorption patterns")
    print(f"      - RMS variation across samples: {stats_df['RMS'].std():.4f}")
    
    # Finding 2: Sample variability
    print(f"\n   2. Inter-Sample Variability:")
    rms_cv = (stats_df['RMS'].std() / stats_df['RMS'].mean()) * 100
    print(f"      - RMS coefficient of variation: {rms_cv:.2f}%")
    if rms_cv < 15:
        print(f"      - ✓ Low variability - consistent fiber properties across samples")
    elif rms_cv < 30:
        print(f"      - ⚠ Moderate variability - some process inconsistency")
    else:
        print(f"      - ❗ High variability - significant differences in fiber/treatment conditions")
    
    # Finding 3: Signal strength patterns
    print(f"\n   3. Signal Strength Patterns:")
    if len(stats_df) > 0 and 'Group' in stats_df.columns:
        group_means = stats_df.groupby('Group')['RMS'].mean().sort_values(ascending=False)
        if len(group_means) > 0:
            strongest = group_means.index[0]
            weakest = group_means.index[-1]
            print(f"      - Strongest signal group: {strongest} (RMS={group_means.iloc[0]:.4f})")
            print(f"      - Weakest signal group: {weakest} (RMS={group_means.iloc[-1]:.4f})")
            print(f"      - Interpretation: May indicate differences in fiber density, surface properties, or degumming extent")
    
    print(f"\n💡 Recommendations:")
    print(f"\n   1. Signal Processing:")
    print(f"      - Current filtering appears effective (negative bias indicates proper reflection capture)")
    print(f"      - Consider bandpass filtering to isolate fiber-specific frequency components")
    print(f"      - Apply wavelet transform for multi-resolution analysis")
    
    print(f"\n   2. Feature Extraction:")
    print(f"      - Extract time-domain features: RMS, peak amplitude, zero-crossing rate")
    print(f"      - Extract frequency-domain features: FFT power spectrum, dominant frequencies")
    print(f"      - Calculate echo delay times to estimate fiber distance/position")
    
    print(f"\n   3. Correlation with Physical Properties:")
    print(f"      - Correlate RMS values with fiber breaking strength (from Break_force.xlsx)")
    print(f"      - Correlate signal energy with extraction rate (from 纤维提取率.xlsx)")
    print(f"      - Use machine learning to predict fiber quality from ultrasonic signatures")
    
    print(f"\n   4. Quality Control Applications:")
    print(f"      - Establish RMS thresholds for quality classification")
    print(f"      - Use signal consistency (CV) as process monitoring indicator")
    print(f"      - Implement real-time defect detection based on anomalous signal patterns")
    
    print(f"\n   5. Advanced Analysis (Future Work):")
    print(f"      - Time-frequency analysis (STFT, Wavelet transform)")
    print(f"      - Echo peak detection and tracking")
    print(f"      - Signal pattern classification using CNN/RNN models")
    print(f"      - Synthetic aperture focusing for 3D fiber imaging")
    
    print("\n" + "=" * 80)
    print("7. STATISTICAL SUMMARY TABLE | 统计汇总表")
    print("=" * 80)
    
    print(f"\n{'Sample':<10} {'Mean':<10} {'Std':<10} {'RMS':<10} {'Min':<10} {'Max':<10} {'P2P':<10}")
    print(f"{'-'*70}")
    
    for idx, row in stats_df.head(20).iterrows():
        print(f"{row['Sample']:<10} {row['Mean']:<10.4f} {row['Std']:<10.4f} {row['RMS']:<10.4f} "
              f"{row['Min']:<10.4f} {row['Max']:<10.4f} {row['Peak2Peak']:<10.4f}")
    
    if len(stats_df) > 20:
        print(f"... ({len(stats_df) - 20} more samples)")
    
    # Save results
    stats_df.to_csv('ultrasonic_signal_stats.csv', index=False, encoding='utf-8-sig')
    print(f"\n💾 Results saved to: ultrasonic_signal_stats.csv")
    
    print("\n" + "=" * 80)
    print("✓ ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nNext Steps:")
    print(f"1. Review signal quality metrics and identify any anomalous samples")
    print(f"2. Correlate ultrasonic features with mechanical properties")
    print(f"3. Develop predictive models linking signal characteristics to fiber quality")
    print(f"4. Implement automated quality control based on ultrasonic signatures")
    print(f"5. Consider advanced signal processing (FFT, wavelet, pattern recognition)")
    print()

if __name__ == "__main__":
    try:
        analyze_ultrasonic_signals()
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
