"""
Use:
    python3 flowClass.py <labeled.csv> <output.csv> <ip1,ip2,...>

"""
import ipaddress
import sys
import pandas as pd

def is_loopback(ip):
    try:
        return ipaddress.ip_address(str(ip)).is_loopback
    except ValueError:
        return False

def classify(src, dst, hosts):
    if is_loopback(src) or is_loopback(dst):
        return "loopback"
    if src in hosts and dst in hosts:
        return "lab_traffic"
    return "background"

def main(in_path, out_path, hosts_arg):
    hosts = {h.strip() for h in hosts_arg.split(",") if h.strip()}
    df = pd.read_csv(in_path, low_memory=False)
    df["flow_class"] = [classify(s, d, hosts) for s, d in zip(df["src_ip"], df["dst_ip"])]
    df["keep"] = df["flow_class"] == "lab_traffic"
    df.to_csv(out_path, index=False)

    print("host lab:", sorted(hosts))
    keys = [c for c in ("tool", "scenario", "phase") if c in df.columns]
    tab = df.groupby(keys + ["flow_class"]).size().unstack(fill_value=0)
    tab["total"] = tab.sum(axis=1)
    print(tab.to_string())
    print(f"\nkeep=True: {int(df['keep'].sum())} from {len(df)}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
