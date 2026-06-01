import json
import os
import matplotlib.pyplot as plt

# 맥 전용 한글 폰트 및 마이너스 깨짐 방지 세팅
plt.rcParams['font.family'] = 'AppleGothic'  
plt.rcParams['axes.unicode_minus'] = False    

DATA_FILE = "swim_records_detailed.json"

VALID_EVENTS = {
    "1": "자유형(Free) 50m",
    "2": "자유형(Free) 100m",
    "3": "배영(Back) 50m",
    "4": "배영(Back) 100m",
    "5": "평영(Breast) 50m",
    "6": "평영(Breast) 100m",
    "7": "접영(Fly) 50m",
    "8": "접영(Fly) 100m"
}

def str_to_seconds(time_str):
    """'1:03.00' -> 63.0 또는 '56.6' -> 56.6 형태로 변환"""
    try:
        if ":" in time_str:
            minutes, seconds = time_str.split(":")
            return int(minutes) * 60 + float(seconds)
        return float(time_str)
    except ValueError:
        return None

def seconds_to_str(seconds):
    """63.0 -> '1:03.00' 또는 56.6 -> '56.60s' 형태로 변환"""
    if seconds >= 60:
        minutes = int(seconds // 60)
        rem_seconds = seconds % 60
        return f"{minutes}:{rem_seconds:05.2f}"
    return f"{seconds:.2f}s"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_data(records):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

def show_graphs_by_event(records):
    # 완전 블랙 배경 + 네온 시안 라인 + PB 하이라이트 + 기록 변동성 추적 차트
    if not records:
        print("[!] No log sessions available for visualization.")
        return

    # 종목별 데이터 분류
    event_data = {event: [] for event in VALID_EVENTS.values()}
    for r in records:
        event = r["event"]
        if event in event_data:
            event_data[event].append(r)

    for event, logs in event_data.items():
        if not logs:
            continue  

        matches = [l["match"] for l in logs]
        times = [l["time"] for l in logs]

        # Personal Best (최고 기록) 탐색 (수영은 초가 짧을수록 1등)
        pb_time = min(times)

        # 배경 패치: 전체 외부 및 내부 도화지를 완전 검은색으로 고정
        fig, ax = plt.subplots(figsize=(8.5, 5.2), facecolor="#000000") 
        ax.set_facecolor("#000000")                                  

        # 기존의 청량한 네온 시안 라인 매핑
        ax.plot(matches, times, color='#00f0ff', linewidth=3.5, zorder=1)

        # 데이터 포인트 및 텍스트 레이블 서브 루프
        for i, current_time in enumerate(times):
            marker_color = '#00f0ff'
            marker_size = 9
            
            # 소수점 내부 데이터를 '분:초' 또는 '초' 형태의 레이블용 문자열로 가공
            formatted_time = seconds_to_str(current_time)
            
            # 최고 기록(PB)인 지점은 샛노란 골드로 하이라이트 칩 적용 (이모지 제거)
            if current_time == pb_time:
                marker_color = '#ffd700' 
                marker_size = 13         
                label_text = f"[PB]\n{formatted_time}"
                text_color = '#ffd700'
            else:
                label_text = formatted_time
                text_color = 'white'

            # 이전 대회 대비 기록 단축 시간 자동 계산 (이모지 제거)
            if i > 0:
                diff = current_time - times[i-1]
                if diff < 0:
                    label_text += f"\n({diff:.2f}s!)"
                elif diff > 0:
                    label_text += f"\n(+{diff:.2f}s)"
                else:
                    label_text += "\n(0.00s)"

            # 데이터 점 플로팅
            ax.scatter(matches[i], current_time, color=marker_color, s=marker_size**2, zorder=2)

            # 텍스트 레이블 매핑
            ax.annotate(label_text, (matches[i], current_time), 
                        textcoords="offset points", xytext=(0, 14), ha='center', 
                        color=text_color, weight='bold', fontsize=10.5)

        # 블랙 배경 인터페이스 맞춤 고대비 폰트 셋업
        ax.set_title(f"{event} - Performance Analysis", color='#00f0ff', fontsize=15, pad=22, weight='bold')
        ax.set_ylabel("Time (Seconds)", color='#aaaaaa', fontsize=11, labelpad=10)
        ax.set_xlabel("Race Session", color='#aaaaaa', fontsize=11, labelpad=12)
        
        # Y축 눈금도 초 단위 숫자가 아닌 분:초 형식 문자열로 맵핑하여 직관성 고도화
        yticks = ax.get_yticks()
        ax.set_yticks(yticks)
        ax.set_yticklabels([seconds_to_str(y) for y in yticks])
        
        # 완전 블랙 격자선 최적화
        ax.tick_params(colors='white', labelsize=10.5)
        ax.grid(True, color="#252525", linestyle="--", alpha=0.6)
        
        # Y축 반전 (초가 클수록 아래로 내려감)
        ax.invert_yaxis() 

        print(f"[SYSTEM] Displaying high-contrast chart for [{event}]...")
        plt.tight_layout()  
        plt.show()  

def main():
    records = load_data()
    
    print("==================================================")
    print("  Swim Analytics Dashboard ")
    print("==================================================")
    print(f"[*] Total loaded log profiles: {len(records)}")
    
    while True:
        print("\n[Menu] 1. Input New Race Session (2 Events) | 2. View Performance Charts | 3. Exit")
        choice = input(">> Select Option: ").strip()

        if choice == "1":
            print("\n--- Race Injection Protocol Initiated ---")
            match = input("• Enter Race Name: ").strip()
            if not match:
                print("[!] Error: Race Name signature is required.")
                continue

            entered_count = 0
            while entered_count < 2:
                print(f"\n[Select Event - {entered_count + 1}/2]")
                print(" 1. Free 50m   | 2. Free 100m\n 3. Back 50m   | 4. Back 100m\n 5. Breast 50m | 6. Breast 100m\n 7. Fly 50m    | 8. Fly 100m")
                event_idx = input("• Choose Event Number: ").strip()

                if event_idx not in VALID_EVENTS:
                    print("[!] Exception: Undefined event number. Try again.")
                    continue
                
                selected_event = VALID_EVENTS[event_idx]

                # 콜론 문자열을 포함한 입력을 처리하기 위해 구문 변경
                raw_time = input(f" [{selected_event}] Enter Time: ").strip()
                time_val = str_to_seconds(raw_time)

                if time_val is None:
                    print("[!] Format Error: Use float numbers or MM:SS.hh format.")
                    continue

                records.append({
                    "match": match,
                    "event": selected_event,
                    "time": time_val
                })
                entered_count += 1
                print(f"[SYSTEM] Dynamic buffer updated for {selected_event}.")

            save_data(records)
            print(f"\n[SUCCESS] Race session '{match}' successfully committed to JSON DB.")

        elif choice == "2":
            show_graphs_by_event(records)

        elif choice == "3":
            print("\n[SYSTEM] Deactivating monitor shell environment. Safe zone closed.")
            break
        else:
            print("[!] Unknown command sequence.")

if __name__ == "__main__":
    main()