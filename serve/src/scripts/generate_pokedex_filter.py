#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成用于图鉴筛选的数据文件
以 WordInfo.json 中的名字为准，确保数据唯一
"""

import json
import os
import glob

def get_generation(index):
    """根据编号获取世代"""
    try:
        num = int(index.split('.')[0])
    except:
        return "未知"
    if num <= 151:
        return "第一世代"
    elif num <= 251:
        return "第二世代"
    elif num <= 386:
        return "第三世代"
    elif num <= 493:
        return "第四世代"
    elif num <= 649:
        return "第五世代"
    elif num <= 721:
        return "第六世代"
    elif num <= 809:
        return "第七世代"
    elif num <= 905:
        return "第八世代"
    else:
        return "第九世代"

def get_evolution_stage(pokemon):
    """获取进化阶段"""
    chains = pokemon.get('evolution_chains', [])
    if not chains or len(chains) == 0:
        return "无进化"
    
    chain = chains[0]
    name = pokemon['name']
    
    for evo in chain:
        if evo['name'] == name:
            stage = evo.get('stage', '')
            if stage == '未进化':
                return '未进化'
            elif stage == '幼年':
                return '幼年'
            elif stage == '1阶进化':
                return '1阶进化'
            elif stage == '2阶进化':
                return '2阶进化'
    
    if len(chain) == 1:
        return "无进化"
    
    return "未知"

def parse_stat(stat_str):
    try:
        return int(stat_str)
    except:
        return 0

def parse_catch_rate(catch_rate):
    if not catch_rate:
        return 0
    try:
        return int(catch_rate.get('number', '0'))
    except:
        return 0

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    pokemon_dir = os.path.join(data_dir, 'pokemon')
    web_json_dir = os.path.join(script_dir, '..', '..', '..', 'web', 'src', 'assets', 'json')
    
    # 读取 WordInfo.json 获取有效的宝可梦名字列表
    wordinfo_path = os.path.join(web_json_dir, 'WordInfo.json')
    with open(wordinfo_path, 'r', encoding='utf-8') as f:
        wordinfo = json.load(f)
    
    # 提取名字列表（新格式是对象数组）
    valid_names = set()
    for item in wordinfo:
        if isinstance(item, dict):
            valid_names.add(item['name'])
        else:
            valid_names.add(item)
    
    print(f"WordInfo.json 中有 {len(valid_names)} 个有效名字")
    
    # 建立名字到文件的映射
    name_to_file = {}
    pokemon_files = glob.glob(os.path.join(pokemon_dir, '*.json'))
    
    for filepath in pokemon_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                pokemon = json.load(f)
            name = pokemon.get('name', '')
            if name in valid_names and name not in name_to_file:
                name_to_file[name] = filepath
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
    
    print(f"找到 {len(name_to_file)} 个匹配的宝可梦文件")
    
    # 收集数据
    pokedex_filter = []
    all_types = set()
    all_colors = set()
    all_shapes = set()
    all_egg_groups = set()
    all_abilities = set()
    
    for name in valid_names:
        if name not in name_to_file:
            print(f"警告: 找不到 {name} 的数据文件")
            continue
        
        filepath = name_to_file[name]
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                pokemon = json.load(f)
            
            if not pokemon.get('forms') or len(pokemon['forms']) == 0:
                continue
            
            form = pokemon['forms'][0]
            
            # 获取特性
            abilities = [ab['name'] for ab in form.get('ability', [])]
            all_abilities.update(abilities)
            
            # 获取进化阶段
            evo_stage = get_evolution_stage(pokemon)
            
            # 获取种族值
            stats = {}
            if pokemon.get('stats') and len(pokemon['stats']) > 0:
                stat_data = pokemon['stats'][0].get('data', {})
                stats = {
                    'hp': parse_stat(stat_data.get('hp', '0')),
                    'attack': parse_stat(stat_data.get('attack', '0')),
                    'defense': parse_stat(stat_data.get('defense', '0')),
                    'sp_attack': parse_stat(stat_data.get('sp_attack', '0')),
                    'sp_defense': parse_stat(stat_data.get('sp_defense', '0')),
                    'speed': parse_stat(stat_data.get('speed', '0')),
                }
                stats['total'] = sum(stats.values())
            
            catch_rate = parse_catch_rate(form.get('catch_rate'))
            
            entry = {
                'name': name,  # 使用名字作为唯一标识
                'index': pokemon['index'],
                'types': form.get('types', []),
                'color': form.get('color', ''),
                'shape': form.get('shape', ''),
                'egg_groups': form.get('egg_groups', []),
                'abilities': abilities,
                'generation': get_generation(pokemon['index']),
                'evolution_stage': evo_stage,
                'stats': stats,
                'catch_rate': catch_rate,
            }
            
            all_types.update(form.get('types', []))
            if form.get('color'):
                all_colors.add(form['color'])
            if form.get('shape'):
                all_shapes.add(form['shape'])
            all_egg_groups.update(form.get('egg_groups', []))
            
            pokedex_filter.append(entry)
        except Exception as e:
            print(f"Error processing {name}: {e}")
    
    # 按 index 排序
    pokedex_filter.sort(key=lambda x: x['index'])
    
    filter_options = {
        'types': sorted(list(all_types)),
        'colors': sorted(list(all_colors)),
        'shapes': sorted(list(all_shapes)),
        'egg_groups': sorted(list(all_egg_groups)),
        'abilities': sorted(list(all_abilities)),
        'generations': [
            "第一世代", "第二世代", "第三世代", "第四世代", "第五世代",
            "第六世代", "第七世代", "第八世代", "第九世代"
        ],
        'evolution_stages': ["幼年", "未进化", "1阶进化", "2阶进化", "无进化"]
    }
    
    output = {
        'options': filter_options,
        'pokemon': pokedex_filter
    }
    
    output_path = os.path.join(web_json_dir, 'PokedexFilter.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"已生成 {output_path}")
    print(f"共处理 {len(pokedex_filter)} 只宝可梦")

if __name__ == '__main__':
    main()
