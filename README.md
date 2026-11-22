# video-subtitle-style-anim

## 题面

给字幕加弹出动效，结果整句一起抖、描边还在缩放时糊成一团：逐字出现时间被统一处理，`per_char` 形同虚设；回弹缓动的端点不在 0/1，`t=0` 有偏移、`t=1` 过冲后不回位；单字缩放走线性插值，回弹感消失；淡入结束时间用 `dur` 而不是 `fade`，淡入拖到缩放结束之后；布局按等宽字体估算，CJK 被当半角，长句一路溢出屏幕；描边宽度直接乘 `scale`，字放大时描边越来越粗、边缘糊成一团；样式校验漏掉 `fade > dur`，淡入未完成缩放就收尾；批量生成复用上一片的字符时间表，第二片从第一片末尾继续；末字时间按 1 基累计，越过字幕显示时间线；`overshoot` 未钳制，参数过大时把单字缩放压成负值。subsfx/animate.py 是核心，tests/test_animate.py 15个红。要修的是：让 `char_times` 从首字起逐字错峰且末字不越界，让 `ease_out_back` 端点精确、回弹受控并钳制 `overshoot`，让 `scale_at` 复用回弹曲线，让 `opacity_at` 只按 `fade_ms` 收口，让 `layout_chars` 按 CJK 全角、拉丁半角累加字宽，让 `stroke_width_at` 始终返回基础描边宽度，让 `validate_style` 检查 `per_char`、`dur`、`fade` 的关系，让 `anim_batch` 为每片独立重排时间线。

## 运行方式

在仓库根目录执行：

```powershell
python -m pytest tests -q
```

初始状态必须恰好是 `15 failed`，并且没有 collection error、import error 或 syntax error。实现完成后应为 `15 passed`。所有时间单位为毫秒，几何单位为像素，数值比较容差为 `1e-9`；运行全程离线，不使用随机数。

## 字段表

| 字段 | 取值 |
| --- | --- |
| 所属领域 | 游戏、图形与多媒体 |
| 子方向 | 音视频处理 |
| 任务类型 | Bugfix |
| 语言/框架 | Python 3, pytest |
| 环境可复现等级 | 无外部依赖 |

## 约束

- `tests/test_animate.py` 不可修改；这 15 条测试就是验收标准。
- 只实现 `subsfx/animate.py` 中的 8 个函数，保持现有函数签名和返回结构；初始状态 8 个函数均抛出 `NotImplementedError`。
- 仅使用 Python 标准库（`math`）与 pytest，离线运行，不使用随机数。
