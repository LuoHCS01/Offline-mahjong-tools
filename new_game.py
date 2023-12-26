import json
import math
import os
import copy

# 役种及拼音简称一览
yizhong = {
    "lz": "立直",
    "dy": "断幺九",
    "zm": "门前清自摸和",
    "mf": "门风牌",
    "cf": "场风牌",
    "b": "白",
    "f": "发",
    "z": "中",
    "ph": "平和",
    "ybk": "一杯口",
    "qg": "抢杠",
    "ls": "岭上开花",
    "haid": "海底捞月",
    "hed": "河底捞鱼",
    "yf": "一发",
    "dbl": "两立直",
    "sstk": "三色同刻",
    "sangz": "三杠子",
    "dd": "对对和",
    "sanak": "三暗刻",
    "xsy": "小三元",
    "hlt": "混老头",
    "qd": "七对子",
    "hq": "混全带幺九",
    "yq": "一气通贯",
    "ssts": "三色同顺",
    "lbk": "二杯口",
    "cq": "纯全带幺九",
    "hys": "混一色",
    "qys": "清一色",
    "ljmg": "流局满贯",
    "th": "天和",
    "dh": "地和",
    "dsy": "大三元",
    "siak": "四暗刻",
    "zys": "字一色",
    "lys": "绿一色",
    "qlt": "清老头",
    "gs": "国士无双",
    "xsx": "小四喜",
    "sigz": "四杠子",
    "jl": "九莲宝灯",
    "sd": "四暗刻单骑",
    "gsssm": "国士无双十三面",
    "czjl": "纯正九莲宝灯",
    "dsx": "大四喜",
}

def new_game():
    print("输入对局名称：", end = "")
    game_name = input()

    print("输入对局类型（默认为半庄）[东风(e)]：", end = "")
    game_type = input()
    if game_type == "e":
        game_type = "东风"
    else:
        game_type = "半庄"

    name_list = json.load(open("玩家昵称表.json", "r", encoding="utf-8"))
    game_players = {}
    print("输入玩家昵称：")
    for loc in ("东家", "南家", "西家", "北家"):
        print(f"{loc}：", end = "")
        player_name = input()
        if player_name in name_list.keys():
            game_players[loc] = name_list[player_name]
        else:
            print(f"输入新玩家全名（留空表示未知全名）：", end = "")
            new_name = input()
            if new_name == "":
                game_players[loc] = f"玩家{'{:0>3d}'.format(name_list['新玩家编号'])}"
                name_list["新玩家编号"] += 1
            else:
                game_players[loc] = new_name
                name_list[player_name] = new_name
    print(f"{game_players}\n请确认玩家全名是否正确？[否(n)]：", end = "")
    right_name = input()
    if right_name == "n":
        exit()
    fw = open("玩家昵称表.json", "w", encoding="utf-8")
    json.dump(name_list, fw, indent=4, ensure_ascii=False)

    game_points = {
        game_players["东家"]: 25000,
        game_players["南家"]: 25000,
        game_players["西家"]: 25000,
        game_players["北家"]: 25000,
    }
    game_info = {
        "场次": "东",
        "局数": 1,
        "本场数": 0,
        "立直棒": 0,
        "点数": game_points
    }
    game = {
        "名称": game_name,
        "游戏类型": game_type,
        "玩家": game_players,
        "对局结果": [],
        "最终点数": {},
    }
    return game, game_info

def new_round(game, game_info):
    round_info = {
        "场次": round_name,
        "胡牌": [],
        "立直": [],
        "局前点数": game_info["点数"].copy(),
        "局后点数": {},
    }
    game_players = list(game["玩家"].values())

    # 根据当前所在位置（东南西北）获取玩家昵称
    def get_players(input_str):
        if input_str == "":
            output_list = []
        else:
            output_list = input_str.split(" ")
            for i in range(len(output_list)):
                index = (int(output_list[i]) + game_info["局数"] - 2) % 4
                output_list[i] = game_players[index]
        return output_list
    
    # 根据是否连庄得出下一局次信息
    def next_round_info(cont_dealer):
        stop_game = False

        if (game["游戏类型"] == "半庄") and (game_info["场次"] == "西"):
            if max(game_info["点数"].values()) >= 30000:
                return True
        if (game["游戏类型"] == "东风") and (game_info["场次"] == "南"):
            if max(game_info["点数"].values()) >= 30000:
                return True

        if not cont_dealer:
            game_info["局数"] = game_info["局数"] % 4 + 1
            if game_info["局数"] == 1:
                # 询问是否西入/南入
                if game["游戏类型"] == "半庄":
                    if game_info["场次"] == "东":
                        game_info["场次"] = "南"
                    elif game_info["场次"] == "南":
                        if max(game_info["点数"].values()) < 30000:
                            print("\n还未有玩家达到30000分，是否西入？[是(y)]：", end = "")
                            west_in = input()
                            if west_in == "y":
                                game_info["场次"] = "西"
                            else:
                                stop_game = True
                        else:
                            stop_game = True
                    elif game_info["场次"] == "西":
                        stop_game = True
                if game["游戏类型"] == "东风":
                    if game_info["场次"] == "东":
                        if max(game_info["点数"].values()) < 30000:
                            print("\n还未有玩家达到30000分，是否南入？[是(y)]：", end = "")
                            south_in = input()
                            if south_in == "y":
                                game_info["场次"] = "南"
                            else:
                                stop_game = True
                    elif game_info["场次"] == "南":
                        stop_game = True

        # 询问击飞后游戏是否结束
        if min(list(game_info["点数"].values())) < 0:
            print("\n已有玩家被击飞，游戏是否继续？[是(y)]：", end = "")
            stop = input()
            stop_game = False if stop == "y" else True
        return stop_game

    # 计算打点
    def get_point(owndraw, yiman, fan, fu):
        if yiman > 0:
            point_p = 8000 * yiman
            point_d = 16000 * yiman
            point_fp = 32000 * yiman
            point_fd = 48000 * yiman
            return point_p, point_d, point_fp, point_fd
        if fan >= 13:
            point_p = 8000
            point_d = 16000
            point_fp = 32000
            point_fd = 48000
        if fan >= 11 and fan <= 12:
            point_p = 6000
            point_d = 12000
            point_fp = 24000
            point_fd = 36000
        if fan >= 8 and fan <= 10:
            point_p = 4000
            point_d = 8000
            point_fp = 16000
            point_fd = 24000
        if fan >= 6 and fan <= 7:
            point_p = 3000
            point_d = 6000
            point_fp = 12000
            point_fd = 18000
        if fan == 5:
            point_p = 2000
            point_d = 4000
            point_fp = 8000
            point_fd = 12000
        if fan <= 4:
            if owndraw:
                point_p = min(math.ceil(0.04 * fu * 2 ** fan) * 100, 2000)
                point_d = min(math.ceil(0.08 * fu * 2 ** fan) * 100, 4000)
                point_fp = 0
                point_fd = 0
            else:
                point_p = 0
                point_d = 0
                point_fp = min(math.ceil(0.16 * fu * 2 ** fan) * 100, 8000)
                point_fd = min(math.ceil(0.24 * fu * 2 ** fan) * 100, 12000)
        return point_p, point_d, point_fp, point_fd

    # 胡牌信息
    def win_info(win, num_cont_dealer):
        yizhong_str = ""
        for (key, value) in yizhong.items():
            yizhong_str += f"{value}({key}), "
        yizhong_str = yizhong_str[:-2]
        print(f"役种（用空格分隔）[{yizhong_str}]：")
        win_yizhong = input()
        win_yizhong = win_yizhong.split(" ")
        for yi in win_yizhong:
            win["役种"].append(yizhong[yi])
        
        print("Dora：", end = "")
        win["Dora"] = int(input())
        print("Aka：", end = "")
        win["Aka"] = int(input())
        print("Ura：", end = "")
        win["Ura"] = int(input())
        print("番数[x番(x)/x倍役满(xbym)]：", end = "")
        win["番数"] = input()
        yiman = 0
        if (win["番数"][-3:] == "bym"):
            fan = 0
            yiman = int(win['番数'][:-3])
            win["番数"] = f"{yiman}倍役满"
        else:
            fan = int(win["番数"])
            win["番数"] = int(win["番数"])
        print("符数：", end = "")
        fu = int(input())
        win["符数"] = fu
        
        dealer = get_players("1")[0]
        if win["是否自摸"] == "是":
            point_p, point_d, _, _ = get_point(True, yiman, fan, fu)
            if win["胡牌者"] == dealer:
                win["打点"] = point_d * 3
                for player in game_players:
                    if player == win["胡牌者"]:
                        game_info["点数"][player] += win["打点"] + game_info["本场数"] * 300
                    else:
                        game_info["点数"][player] -= point_d + game_info["本场数"] * 100
            else:
                win["打点"] = point_p * 2 + point_d
                for player in game_players:
                    if player == win["胡牌者"]:
                        game_info["点数"][player] += win["打点"] + game_info["本场数"] * 300
                    else:
                        if player == dealer:
                            game_info["点数"][player] -= point_d + game_info["本场数"] * 100
                        else:
                            game_info["点数"][player] -= point_p + game_info["本场数"] * 100
        else:
            _, _, point_fp, point_fd = get_point(False, yiman, fan, win["符数"])
            if win["胡牌者"] == dealer:
                win["打点"] = point_fd
            else:
                win["打点"] = point_fp
            # 此处需要注意本场棒头跳
            game_info["点数"][win["胡牌者"]] += win["打点"] + num_cont_dealer * 300
            game_info["点数"][win["放铳者"]] -= win["打点"] + num_cont_dealer * 300

        print(f"打点：{win['打点']}")
        round_info["胡牌"].append(win)
    
    # 荒牌流局时不听者需要交罚符
    def penalty(ready_players):
        for i in range(len(game["玩家"])):
            player = game_players[i]
            if player in ready_players:
                game_info["点数"][player] += int(3000 / len(ready_players))
            else:
                game_info["点数"][player] -= int(3000 / (4 - len(ready_players)))

    print("\n立直家（用空格分隔）[东家(1)，南家(2)，西家(3), 北家(4)]：", end = "")
    reach_players = input()
    reach_players = get_players(reach_players)
    round_info["立直"] = reach_players
    for i in range(len(reach_players)):
        game_info["点数"][reach_players[i]] -= 1000
        game_info["立直棒"] += 1

    print("是否流局[是(y)/否(n)]：", end = "")
    draw = input()
    if draw == "y":
        game_info["本场数"] += 1
        print("流局类型（默认荒牌流局）[四风连打(sf)/四杠散了(sg)/九种九牌(jj)/四家立直(sl)]：", end = "")
        draw_type = input()

        stop_game = False
        if draw_type == "":
            print("听牌者（用空格分隔）[东家(1)，南家(2)，西家(3), 北家(4)]：", end = "")
            ready_players = input()
            ready_players = get_players(ready_players)
            if (len(ready_players) >= 1) and (len(ready_players) <= 3):
                penalty(ready_players)
            dealer = get_players("1")[0]
            stop_game = next_round_info(dealer in ready_players)

        round_info["局后点数"] = game_info["点数"].copy()
        game["对局结果"].append(round_info)
        return game, game_info, stop_game
    
    # elif draw == "n":
    print("胡牌者（一炮多响用空格分隔）[东家(1)，南家(2)，西家(3), 北家(4)]：", end = "")
    win_players_index = input()
    win_players = get_players(win_players_index)

    print("放铳者（不填表示自摸）[东家(1)/南家(2)/西家(3)/北家(4)]：", end = "")
    fire_player = input()

    if len(win_players) == 1:
        win = {
            "胡牌者": win_players[0],
            "是否自摸": "",
            "放铳者": "",
            "役种": [],
            "Dora": 0,
            "Aka": 0,
            "Ura": 0,
            "番数": 0,
            "符数": 0,
            "打点": 0,
        }

        if fire_player == "":
            win["是否自摸"] = "是"
        else:
            win["是否自摸"] = "否"
            win["放铳者"] = get_players(fire_player)[0]
        win_info(win, game_info["本场数"])
        
        # 给付立直棒
        game_info["点数"][win["胡牌者"]] += game_info["立直棒"] * 1000
        game_info["立直棒"] = 0

    # 处理一炮多响
    if len(win_players) > 1:
        fire_player_index = int(fire_player)
        fire_player = get_players(fire_player)[0]
        win_index = 1
        num_cont_dealer = game_info["本场数"]
        for i in range(fire_player_index + 1, fire_player_index + 4):
            index = str(((i - 1) % 4) + 1)
            if index in win_players_index.split(" "):
                str_win_index = {
                    "1": "东家",
                    "2": "南家",
                    "3": "西家",
                    "4": "北家",
                }
                print(f"\n第{win_index}位胡牌者[{str_win_index[index]}]：")

                win = {
                    "胡牌者": get_players(index)[0],
                    "是否自摸": "否",
                    "放铳者": fire_player,
                    "役种": [],
                    "Dora": 0,
                    "Aka": 0,
                    "Ura": 0,
                    "番数": 0,
                    "符数": 0,
                    "打点": 0,
                }

                # 本场数供托、立直棒头跳
                game_info["点数"][win["胡牌者"]] += num_cont_dealer * 300 + game_info["立直棒"] * 1000
                game_info["点数"][win["放铳者"]] -= num_cont_dealer * 300
                num_cont_dealer = 0
                game_info["立直棒"] = 0

                win_info(win, 0)
                win_index += 1

    round_info["局后点数"] = game_info["点数"].copy()
    game["对局结果"].append(round_info)

    cont_dealer = False
    if "1" in win_players_index.split(" "):
        cont_dealer = True
    if cont_dealer:
        game_info["本场数"] += 1
    else:
        game_info["本场数"] = 0
    stop_game = next_round_info(cont_dealer)
    return game, game_info, stop_game

if __name__ == "__main__":
    print("是否载入未完成的对局[是(y)]：", end = "")
    load = input()
    if load == "y":
        print("输入对局名称：", end = "")
        name = input()
        game = json.load(open(f"./data/{name}.json", "r", encoding="utf-8"))
        game_his = json.load(open(f"./data/{name}_his.json", "r", encoding="utf-8"))
        game_info = copy.deepcopy(game_his[-1])
    else:
        game, game_info = new_game()
        game_his = []
        temp = copy.deepcopy(game_info)
        game_his.append(temp)

        fw = open(f"./data/{game['名称']}.json", "w", encoding="utf-8")
        json.dump(game, fw, indent=4, ensure_ascii=False)
        fw.close()
        fw = open(f"./data/{game['名称']}_his.json", "w", encoding="utf-8")
        json.dump(game_his, fw, indent=4, ensure_ascii=False)
        fw.close()
    print("\nGame Start!")

    stop_game = False
    while not stop_game:
        round_name = f"{game_info['场次']}{game_info['局数']}局{game_info['本场数']}本场"
        print(f"\n========================={round_name}=========================\n\n当前点数：{game_info['点数']}，立直棒：{game_info['立直棒']}\n")

        print("开始记录本局，或回退至上一局[回退(b)]：", end = "")
        back = input()
        if back == "b":
            game = json.load(open(f"./data/{game['名称']}.json", "r", encoding="utf-8"))
            game_his = json.load(open(f"./data/{game['名称']}_his.json", "r", encoding="utf-8"))
            if len(game_his) > 1:
                game_his = game_his[:-1]
                game["对局结果"] = game["对局结果"][:-1]
                game_info = copy.deepcopy(game_his[-1])

                fw = open(f"./data/{game['名称']}.json", "w", encoding="utf-8")
                json.dump(game, fw, indent=4, ensure_ascii=False)
                fw.close()
                fw = open(f"./data/{game['名称']}_his.json", "w", encoding="utf-8")
                json.dump(game_his, fw, indent=4, ensure_ascii=False)
                fw.close()
            else:
                print("\n已经到头了，无法回退！")
        else:
            game, game_info, stop_game = new_round(game, game_info)

            fw = open(f"./data/{game['名称']}.json", "w", encoding="utf-8")
            json.dump(game, fw, indent=4, ensure_ascii=False)
            fw.close()
            fw = open(f"./data/{game['名称']}_his.json", "w", encoding="utf-8")
            temp = copy.deepcopy(game_info)
            game_his.append(temp)
            json.dump(game_his, fw, indent=4, ensure_ascii=False)
            fw.close()

    # 对局结束后一位获得场上未确认归属的立直棒
    max_index = 0
    for i in range(4):
        if list(game_info["点数"].values())[max_index] < list(game_info["点数"].values())[i]:
            max_index = i
    game_info["点数"][list(game["玩家"].values())[max_index]] += game_info["立直棒"] * 1000
    
    game["最终点数"] = game_info["点数"].copy()
    print(f"\nGame over!\n\n最终点数：{game_info['点数']}\n")
    fw = open(f"./data/{game['名称']}.json", "w", encoding="utf-8")
    json.dump(game, fw, indent=4, ensure_ascii=False)
    fw.close()
    os.remove(f"./data/{game['名称']}_his.json")