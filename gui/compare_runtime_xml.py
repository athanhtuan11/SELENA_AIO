#!/usr/bin/env python3
"""Compare two SELENA runtime XML files and show key differences."""

import xml.etree.ElementTree as ET
from collections import defaultdict
import sys
import pandas as pd
from datetime import datetime

def parse_xml(filepath):
    """Parse XML and extract key information."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    data = {
        'runnables': {},
        'connections': [],
        'jobs': defaultdict(list)
    }
    
    # Extract runnable configurations - capture ALL child elements
    for runnable in root.findall('.//runnable[@name]'):
        name = runnable.get('name')
        config = {
            'attributes': {},
            'children': {}
        }
        
        # Get all attributes of runnable tag
        for attr, value in runnable.attrib.items():
            if attr != 'name':
                config['attributes'][attr] = value
        
        # Get all child elements with their attributes
        for child in runnable:
            tag = child.tag
            if tag not in config['children']:
                config['children'][tag] = []
            
            child_data = {'text': child.text.strip() if child.text else None}
            # Add all attributes
            for attr, value in child.attrib.items():
                child_data[attr] = value
            
            config['children'][tag].append(child_data)
        
        data['runnables'][name] = config
    
    # Extract connections with ALL attributes
    for conn in root.findall('.//connection'):
        outport = conn.find('outport')
        inport = conn.find('inport')
        
        if outport is not None and inport is not None:
            conn_data = {
                'from_runnable': outport.get('runnable'),
                'from_port': outport.get('port'),
                'to_runnable': inport.get('runnable'),
                'to_port': inport.get('port'),
                'outport_attrs': dict(outport.attrib),  # All outport attributes
                'inport_attrs': dict(inport.attrib),    # All inport attributes
            }
            
            # Remove runnable/port from attrs dict as they're already extracted
            conn_data['outport_attrs'].pop('runnable', None)
            conn_data['outport_attrs'].pop('port', None)
            conn_data['inport_attrs'].pop('runnable', None)
            conn_data['inport_attrs'].pop('port', None)
            
            # Extract child elements (doorkeeper, systemtime, time_compare, etc) 
            # These are SIBLINGS of outport/inport, not children!
            conn_data['connection_children'] = {}
            for child in conn:
                if child.tag in ['outport', 'inport']:
                    continue  # Skip, already processed
                
                tag = child.tag
                child_data = dict(child.attrib)
                if child.text and child.text.strip():
                    child_data['_text'] = child.text.strip()
                
                # Extract grandchildren (e.g., inport_key, outport_key under doorkeeper)
                for grandchild in child:
                    gc_tag = grandchild.tag
                    gc_data = dict(grandchild.attrib)
                    if grandchild.text and grandchild.text.strip():
                        gc_data['_text'] = grandchild.text.strip()
                    if gc_tag not in child_data:
                        child_data[gc_tag] = []
                    child_data[gc_tag].append(gc_data)
                
                conn_data['connection_children'][tag] = child_data
            
            data['connections'].append(conn_data)
    
    # Extract job assignments
    for job in root.findall('.//job'):
        task = job.get('task')
        mode = job.get('mode', 'cyclic')
        for runnable in job.findall('runnable'):
            name = runnable.get('name')
            data['jobs'][task].append((name, mode))
    
    return data

def compare_runnables(file1_data, file2_data, file1_name, file2_name):
    """Compare runnable configurations."""
    print("=" * 80)
    print("RUNNABLE CONFIGURATION DIFFERENCES (ALL ATTRIBUTES)")
    print("=" * 80)
    
    all_runnables = set(file1_data['runnables'].keys()) | set(file2_data['runnables'].keys())
    
    only_in_1 = []
    only_in_2 = []
    different = []
    
    for runnable in sorted(all_runnables):
        config1 = file1_data['runnables'].get(runnable)
        config2 = file2_data['runnables'].get(runnable)
        
        if config1 is None:
            only_in_2.append(runnable)
            continue
        if config2 is None:
            only_in_1.append(runnable)
            continue
        
        # Check for differences in ALL attributes and children
        differences = []
        
        # Compare attributes
        if config1['attributes'] != config2['attributes']:
            attrs1 = config1['attributes']
            attrs2 = config2['attributes']
            all_attr_keys = set(attrs1.keys()) | set(attrs2.keys())
            for key in all_attr_keys:
                if attrs1.get(key) != attrs2.get(key):
                    differences.append(f"  attribute '{key}': {attrs1.get(key)} vs {attrs2.get(key)}")
        
        # Compare children tags
        all_child_tags = set(config1['children'].keys()) | set(config2['children'].keys())
        
        for tag in all_child_tags:
            children1 = config1['children'].get(tag, [])
            children2 = config2['children'].get(tag, [])
            
            if len(children1) != len(children2):
                differences.append(f"  <{tag}>: count {len(children1)} vs {len(children2)}")
            elif children1 != children2:
                # Detailed comparison of child elements
                for i, (c1, c2) in enumerate(zip(children1, children2)):
                    if c1 != c2:
                        diff_attrs = []
                        all_keys = set(c1.keys()) | set(c2.keys())
                        for key in all_keys:
                            if c1.get(key) != c2.get(key):
                                diff_attrs.append(f"{key}: '{c1.get(key)}' vs '{c2.get(key)}'")
                        if diff_attrs:
                            differences.append(f"  <{tag}>[{i}]: {', '.join(diff_attrs)}")
        
        if differences:
            different.append((runnable, differences))
    
    # Print results
    if only_in_1:
        print(f"\n[ONLY IN {file1_name}]: {len(only_in_1)} runnables")
        for r in only_in_1[:10]:  # Show first 10
            print(f"  - {r}")
        if len(only_in_1) > 10:
            print(f"  ... and {len(only_in_1) - 10} more")
    
    if only_in_2:
        print(f"\n[ONLY IN {file2_name}]: {len(only_in_2)} runnables")
        for r in only_in_2[:10]:
            print(f"  - {r}")
        if len(only_in_2) > 10:
            print(f"  ... and {len(only_in_2) - 10} more")
    
    if different:
        print(f"\n[DIFFERENT CONFIGURATIONS]: {len(different)} runnables")
        print("\nShowing all differences:")
        for runnable, diffs in different:
            print(f"\n  [{runnable}]")
            for diff in diffs:
                print(f"    {diff}")
    
    if not only_in_1 and not only_in_2 and not different:
        print("\n✅ ALL runnable configurations are IDENTICAL!")
    
    print(f"\n[SUMMARY]")
    print(f"  Total runnables: {len(all_runnables)}")
    print(f"  Identical: {len(all_runnables) - len(only_in_1) - len(only_in_2) - len(different)}")
    print(f"  Different: {len(different)}")
    print(f"  Only in {file1_name}: {len(only_in_1)}")
    print(f"  Only in {file2_name}: {len(only_in_2)}")

def compare_connections(file1_data, file2_data, file1_name, file2_name):
    """Compare connection configurations with ALL attributes."""
    print("\n" + "=" * 80)
    print("CONNECTION DIFFERENCES - COMPREHENSIVE (ALL ATTRIBUTES)")
    print("=" * 80)
    
    # Option to filter or show all
    show_all = False  # Set to True to see ALL connections
    keywords = ['AntDiag', 'DspRunnable', 'g_DspRunnable']
    
    def is_relevant(conn):
        if show_all:
            return True
        return any(kw in str(conn.values()) for kw in keywords)
    
    def conn_signature(conn):
        """Create unique signature for connection comparison."""
        return (
            conn['from_runnable'],
            conn['from_port'],
            conn['to_runnable'],
            conn['to_port']
        )
    
    def format_attrs(attrs_dict):
        """Format attributes for display."""
        parts = []
        for k, v in sorted(attrs_dict.items()):
            parts.append(f"{k}={v}")
        return ', '.join(parts) if parts else 'none'
    
    def conn_str(conn, show_attrs=True):
        """Format connection as string with all details."""
        base = f"  {conn['from_runnable']}.{conn['from_port']} -> {conn['to_runnable']}.{conn['to_port']}"
        if not show_attrs:
            return base
        
        out_attrs = format_attrs(conn['outport_attrs'])
        in_attrs = format_attrs(conn['inport_attrs'])
        conn_children = conn.get('connection_children', {})
        
        details = []
        if out_attrs != 'none':
            details.append(f"OUT[{out_attrs}]")
        if in_attrs != 'none':
            details.append(f"IN[{in_attrs}]")
        
        # Add doorkeeper info
        if 'doorkeeper' in conn_children:
            dk = conn_children['doorkeeper']
            dk_str = f"doorkeeper={dk.get('modus', '?')}"
            details.append(f"DK[{dk_str}]")
        
        if details:
            return f"{base}\n    {' | '.join(details)}"
        return base
    
    conns1 = [c for c in file1_data['connections'] if is_relevant(c)]
    conns2 = [c for c in file2_data['connections'] if is_relevant(c)]
    
    # Create sets of connection signatures
    sigs1 = {conn_signature(c): c for c in conns1}
    sigs2 = {conn_signature(c): c for c in conns2}
    
    # Find differences
    only_in_1 = set(sigs1.keys()) - set(sigs2.keys())
    only_in_2 = set(sigs2.keys()) - set(sigs1.keys())
    common = set(sigs1.keys()) & set(sigs2.keys())
    
    # Check for ALL attribute differences in common connections
    attr_diffs = []
    for sig in common:
        c1 = sigs1[sig]
        c2 = sigs2[sig]
        
        diffs = []
        
        # Compare outport attributes
        if c1['outport_attrs'] != c2['outport_attrs']:
            all_keys = set(c1['outport_attrs'].keys()) | set(c2['outport_attrs'].keys())
            for key in all_keys:
                v1 = c1['outport_attrs'].get(key)
                v2 = c2['outport_attrs'].get(key)
                if v1 != v2:
                    diffs.append(f"outport.{key}: '{v1}' vs '{v2}'")
        
        # Compare inport attributes
        if c1['inport_attrs'] != c2['inport_attrs']:
            all_keys = set(c1['inport_attrs'].keys()) | set(c2['inport_attrs'].keys())
            for key in all_keys:
                v1 = c1['inport_attrs'].get(key)
                v2 = c2['inport_attrs'].get(key)
                if v1 != v2:
                    diffs.append(f"inport.{key}: '{v1}' vs '{v2}'")
        
        # Compare connection children (doorkeeper, systemtime, etc)
        if c1['connection_children'] != c2['connection_children']:
            all_tags = set(c1['connection_children'].keys()) | set(c2['connection_children'].keys())
            for tag in all_tags:
                v1 = c1['connection_children'].get(tag)
                v2 = c2['connection_children'].get(tag)
                if v1 != v2:
                    # Format doorkeeper differences more clearly
                    if tag == 'doorkeeper':
                        m1 = v1.get('modus') if v1 else None
                        m2 = v2.get('modus') if v2 else None
                        diffs.append(f"<doorkeeper>: modus '{m1}' vs '{m2}'")
                    else:
                        diffs.append(f"<{tag}>: {v1} vs {v2}")
        
        if diffs:
            attr_diffs.append((sig, diffs))
    
    if only_in_1:
        print(f"\n[ONLY IN {file1_name}]: {len(only_in_1)}")
        for sig in sorted(only_in_1):
            print(conn_str(sigs1[sig], show_attrs=True))
    
    if only_in_2:
        print(f"\n[ONLY IN {file2_name}]: {len(only_in_2)}")
        for sig in sorted(only_in_2):
            print(conn_str(sigs2[sig], show_attrs=True))
    
    if attr_diffs:
        print(f"\n[DIFFERENT ATTRIBUTES]: {len(attr_diffs)} connections")
        for sig, diffs in attr_diffs:
            c1 = sigs1[sig]
            c2 = sigs2[sig]
            print(f"\n  {c1['from_runnable']}.{c1['from_port']} -> {c1['to_runnable']}.{c1['to_port']}")
            for diff in diffs:
                print(f"    • {diff}")
    
    if not only_in_1 and not only_in_2 and not attr_diffs:
        print("\n✅ All AntDiag/DspRunnable connections are IDENTICAL!")
    
    print(f"\n[SUMMARY]")
    print(f"  Common connections: {len(common)}")
    print(f"  Identical: {len(common) - len(attr_diffs)}")
    print(f"  Attribute differences: {len(attr_diffs)}")
    print(f"  Only in {file1_name}: {len(only_in_1)}")
    print(f"  Only in {file2_name}: {len(only_in_2)}")

def compare_jobs(file1_data, file2_data, file1_name, file2_name):
    """Compare job task assignments."""
    print("\n" + "=" * 80)
    print("JOB ASSIGNMENT DIFFERENCES (Dsp/AntDiag related)")
    print("=" * 80)
    
    all_tasks = set(file1_data['jobs'].keys()) | set(file2_data['jobs'].keys())
    
    has_diffs = False
    for task in sorted(all_tasks):
        runnables1 = set(r[0] for r in file1_data['jobs'].get(task, []))
        runnables2 = set(r[0] for r in file2_data['jobs'].get(task, []))
        
        # Check for DspRunnable related tasks
        dsp_related = [r for r in (runnables1 | runnables2) if 'Dsp' in r or 'AntDiag' in r]
        
        if dsp_related:
            only_in_1 = [r for r in (runnables1 - runnables2) if 'Dsp' in r or 'AntDiag' in r]
            only_in_2 = [r for r in (runnables2 - runnables1) if 'Dsp' in r or 'AntDiag' in r]
            
            if only_in_1 or only_in_2:
                has_diffs = True
                print(f"\n[TASK: {task}]")
                
                if only_in_1:
                    print(f"  Only in {file1_name}: {', '.join(only_in_1)}")
                if only_in_2:
                    print(f"  Only in {file2_name}: {', '.join(only_in_2)}")
            else:
                # Show identical assignments
                print(f"\n[TASK: {task}] ✅ IDENTICAL")
                for r in sorted(dsp_related):
                    print(f"  - {r}")
    
    if not has_diffs:
        print("\n✅ All Dsp/AntDiag job assignments are IDENTICAL!")

def compare_doorkeepers(file1_data, file2_data, file1_name, file2_name):
    """Compare doorkeeper configurations across all connections."""
    print("\n" + "=" * 80)
    print("DOORKEEPER COMPARISON")
    print("=" * 80)
    
    def get_doorkeeper_info(conn):
        """Extract doorkeeper information from connection."""
        dk = conn['connection_children'].get('doorkeeper')
        if dk:
            return dk
        return None
    
    # Analyze doorkeeper usage
    dk_count1 = sum(1 for c in file1_data['connections'] if 'doorkeeper' in c['connection_children'])
    dk_count2 = sum(1 for c in file2_data['connections'] if 'doorkeeper' in c['connection_children'])
    
    # Count by modus
    dk_modes1 = {}
    dk_modes2 = {}
    
    for conn in file1_data['connections']:
        dk = get_doorkeeper_info(conn)
        if dk:
            modus = dk['modus']
            dk_modes1[modus] = dk_modes1.get(modus, 0) + 1
    
    for conn in file2_data['connections']:
        dk = get_doorkeeper_info(conn)
        if dk:
            modus = dk['modus']
            dk_modes2[modus] = dk_modes2.get(modus, 0) + 1
    
    print(f"\n[{file1_name}] Doorkeeper usage:")
    print(f"  Total connections with doorkeeper: {dk_count1}")
    for modus, count in sorted(dk_modes1.items()):
        print(f"    {modus}: {count}")
    
    print(f"\n[{file2_name}] Doorkeeper usage:")
    print(f"  Total connections with doorkeeper: {dk_count2}")
    for modus, count in sorted(dk_modes2.items()):
        print(f"    {modus}: {count}")
    
    # Compare specific connections
    print(f"\n[DOORKEEPER DIFFERENCES]")
    
    def conn_sig(conn):
        return (conn['from_runnable'], conn['from_port'], conn['to_runnable'], conn['to_port'])
    
    conns1 = {conn_sig(c): c for c in file1_data['connections']}
    conns2 = {conn_sig(c): c for c in file2_data['connections']}
    
    common_sigs = set(conns1.keys()) & set(conns2.keys())
    
    dk_diffs = []
    for sig in common_sigs:
        dk1 = get_doorkeeper_info(conns1[sig])
        dk2 = get_doorkeeper_info(conns2[sig])
        
        if dk1 != dk2:
            dk_diffs.append((sig, dk1, dk2))
    
    if dk_diffs:
        print(f"\n  Found {len(dk_diffs)} connections with doorkeeper differences:")
        for i, (sig, dk1, dk2) in enumerate(dk_diffs[:10]):  # Show first 10
            print(f"\n  [{i+1}] {sig[0]}.{sig[1]} -> {sig[2]}.{sig[3]}")
            print(f"      {file1_name}: {dk1}")
            print(f"      {file2_name}: {dk2}")
        
        if len(dk_diffs) > 10:
            print(f"\n  ... and {len(dk_diffs) - 10} more doorkeeper differences")
    else:
        print("  ✅ All common connections have identical doorkeeper configs")

def export_to_excel(data1, data2, file1_name, file2_name):
    """Export comparison results to Excel with multiple sheets."""
    
    output_file = f"runtime_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        
        # Sheet 1: Runnable Differences
        runnable_data = []
        all_runnables = set(data1['runnables'].keys()) | set(data2['runnables'].keys())
        
        for runnable in sorted(all_runnables):
            config1 = data1['runnables'].get(runnable)
            config2 = data2['runnables'].get(runnable)
            
            if config1 is None:
                runnable_data.append({
                    'Runnable': runnable,
                    file1_name: 'NOT FOUND',
                    file2_name: 'EXISTS',
                    'Difference': 'Only in file2'
                })
            elif config2 is None:
                runnable_data.append({
                    'Runnable': runnable,
                    file1_name: 'EXISTS',
                    file2_name: 'NOT FOUND',
                    'Difference': 'Only in file1'
                })
            elif config1 != config2:
                diff_details = []
                for tag in set(config1['children'].keys()) | set(config2['children'].keys()):
                    if config1['children'].get(tag) != config2['children'].get(tag):
                        diff_details.append(f"{tag} differs")
                
                runnable_data.append({
                    'Runnable': runnable,
                    file1_name: str(config1['children']),
                    file2_name: str(config2['children']),
                    'Difference': '; '.join(diff_details)
                })
        
        df_runnables = pd.DataFrame(runnable_data)
        if not df_runnables.empty:
            df_runnables.to_excel(writer, sheet_name='Runnable_Differences', index=False)
        
        # Sheet 2: Doorkeeper Comparison
        doorkeeper_data = []
        
        def conn_sig(c):
            return (c['from_runnable'], c['from_port'], c['to_runnable'], c['to_port'])
        
        conns1_dict = {conn_sig(c): c for c in data1['connections']}
        conns2_dict = {conn_sig(c): c for c in data2['connections']}
        
        all_conn_sigs = set(conns1_dict.keys()) | set(conns2_dict.keys())
        
        for sig in sorted(all_conn_sigs):
            from_r, from_p, to_r, to_p = sig
            conn_str = f"{from_r}.{from_p} -> {to_r}.{to_p}"
            
            c1 = conns1_dict.get(sig)
            c2 = conns2_dict.get(sig)
            
            dk1 = c1['connection_children'].get('doorkeeper') if c1 else None
            dk2 = c2['connection_children'].get('doorkeeper') if c2 else None
            
            if dk1 != dk2:
                doorkeeper_data.append({
                    'Connection': conn_str,
                    f'{file1_name}_Doorkeeper': dk1.get('modus') if dk1 else 'None',
                    f'{file1_name}_Details': str(dk1) if dk1 else 'N/A',
                    f'{file2_name}_Doorkeeper': dk2.get('modus') if dk2 else 'None',
                    f'{file2_name}_Details': str(dk2) if dk2 else 'N/A',
                    'Status': 'DIFFERENT' if (dk1 and dk2) else 'MISSING' if not dk1 else 'EXTRA'
                })
        
        df_doorkeeper = pd.DataFrame(doorkeeper_data)
        if not df_doorkeeper.empty:
            df_doorkeeper.to_excel(writer, sheet_name='Doorkeeper_Differences', index=False)
        
        # Sheet 3: Connection Differences (Missing/Extra)
        connection_diff_data = []
        
        only_in_1 = set(conns1_dict.keys()) - set(conns2_dict.keys())
        only_in_2 = set(conns2_dict.keys()) - set(conns1_dict.keys())
        
        for sig in sorted(only_in_1):
            from_r, from_p, to_r, to_p = sig
            c1 = conns1_dict[sig]
            dk1 = c1['connection_children'].get('doorkeeper')
            
            connection_diff_data.append({
                'Connection': f"{from_r}.{from_p} -> {to_r}.{to_p}",
                'Status': f'Only in {file1_name}',
                'Doorkeeper': dk1.get('modus') if dk1 else 'None',
                'Inport_Attrs': str(c1['inport_attrs']),
                'Outport_Attrs': str(c1['outport_attrs'])
            })
        
        for sig in sorted(only_in_2):
            from_r, from_p, to_r, to_p = sig
            c2 = conns2_dict[sig]
            dk2 = c2['connection_children'].get('doorkeeper')
            
            connection_diff_data.append({
                'Connection': f"{from_r}.{from_p} -> {to_r}.{to_p}",
                'Status': f'Only in {file2_name}',
                'Doorkeeper': dk2.get('modus') if dk2 else 'None',
                'Inport_Attrs': str(c2['inport_attrs']),
                'Outport_Attrs': str(c2['outport_attrs'])
            })
        
        df_conn_diff = pd.DataFrame(connection_diff_data)
        if not df_conn_diff.empty:
            df_conn_diff.to_excel(writer, sheet_name='Connection_Differences', index=False)
        
        # Sheet 4: Connection Attribute Differences
        attr_diff_data = []
        common_sigs = set(conns1_dict.keys()) & set(conns2_dict.keys())
        
        for sig in sorted(common_sigs):
            from_r, from_p, to_r, to_p = sig
            c1 = conns1_dict[sig]
            c2 = conns2_dict[sig]
            
            diffs = []
            
            # Compare inport attributes
            for key in set(c1['inport_attrs'].keys()) | set(c2['inport_attrs'].keys()):
                v1 = c1['inport_attrs'].get(key)
                v2 = c2['inport_attrs'].get(key)
                if v1 != v2:
                    diffs.append(f"inport.{key}")
            
            # Compare outport attributes
            for key in set(c1['outport_attrs'].keys()) | set(c2['outport_attrs'].keys()):
                v1 = c1['outport_attrs'].get(key)
                v2 = c2['outport_attrs'].get(key)
                if v1 != v2:
                    diffs.append(f"outport.{key}")
            
            if diffs:
                attr_diff_data.append({
                    'Connection': f"{from_r}.{from_p} -> {to_r}.{to_p}",
                    f'{file1_name}_Inport': str(c1['inport_attrs']),
                    f'{file2_name}_Inport': str(c2['inport_attrs']),
                    f'{file1_name}_Outport': str(c1['outport_attrs']),
                    f'{file2_name}_Outport': str(c2['outport_attrs']),
                    'Different_Attributes': ', '.join(diffs)
                })
        
        df_attr_diff = pd.DataFrame(attr_diff_data)
        if not df_attr_diff.empty:
            df_attr_diff.to_excel(writer, sheet_name='Attribute_Differences', index=False)
        
        # Sheet 5: Summary
        summary_data = [
            {'Metric': 'Total Runnables', file1_name: len(data1['runnables']), file2_name: len(data2['runnables'])},
            {'Metric': 'Total Connections', file1_name: len(data1['connections']), file2_name: len(data2['connections'])},
            {'Metric': 'Doorkeeper Count', 
             file1_name: sum(1 for c in data1['connections'] if 'doorkeeper' in c['connection_children']),
             file2_name: sum(1 for c in data2['connections'] if 'doorkeeper' in c['connection_children'])},
            {'Metric': 'Runnable Differences', file1_name: len(runnable_data), file2_name: ''},
            {'Metric': 'Doorkeeper Differences', file1_name: len(doorkeeper_data), file2_name: ''},
            {'Metric': 'Connection Differences', file1_name: len(connection_diff_data), file2_name: ''},
            {'Metric': 'Attribute Differences', file1_name: len(attr_diff_data), file2_name: ''},
        ]
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"\n✅ Excel file exported: {output_file}")
    return output_file

def main():
    file1 = r"d:\suv_ods_R5.3.2\rn_apl\selena\config\runtime\full_runtime_5.3.2_mf4_R5.1.6_local.xml"
    file2 = r"d:\suv_ods_R5.3.2\rn_apl\selena\config\runtime\Full_4_3_1911_1to_SW_5_1_6.xml"
    
    print("Parsing XML files...")
    data1 = parse_xml(file1)
    data2 = parse_xml(file2)
    
    file1_name = "full_runtime_5.3.2_mf4_R5.1.6_local.xml"
    file2_name = "Full_4_3_1911_1to_SW_5_1_6.xml"
    
    compare_runnables(data1, data2, file1_name, file2_name)
    compare_doorkeepers(data1, data2, file1_name, file2_name)
    compare_connections(data1, data2, file1_name, file2_name)
    compare_jobs(data1, data2, file1_name, file2_name)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total runnables in {file1_name}: {len(data1['runnables'])}")
    print(f"Total runnables in {file2_name}: {len(data2['runnables'])}")
    print(f"Total connections in {file1_name}: {len(data1['connections'])}")
    print(f"Total connections in {file2_name}: {len(data2['connections'])}")
    
    # Export to Excel
    print("\n" + "=" * 80)
    print("EXPORTING TO EXCEL")
    print("=" * 80)
    try:
        output_file = export_to_excel(data1, data2, file1_name, file2_name)
        print(f"Excel comparison saved to: {output_file}")
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        print("Make sure pandas and openpyxl are installed: pip install pandas openpyxl")

if __name__ == "__main__":
    main()
