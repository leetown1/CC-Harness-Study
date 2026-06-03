# Buddy 系统深度技术文档

> 基于逐行代码分析的完整技术文档  
> **探索完成时间**: 2026 年 4 月 1 日  
> **核心文件**: buddy/ 目录下 6 个文件

---

## 1. Buddy 系统架构概览

### 1.1 系统职责

Buddy 系统是一个**虚拟伙伴功能**，为用户提供持久的 ASCII 艺术宠物，生活在终端界面中。伙伴会对用户交互做出反应，显示对话气泡，并具有个性特征。这是一个游戏化元素，旨在使编码体验更加 engaging 和个性化。

### 1.2 架构层次

```
┌─────────────────────────────────────────────────────────────┐
│                    Buddy System Architecture                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ companion.ts │  │  sprites.ts  │  │  types.ts    │      │
│  │  (Logic)     │  │  (Visuals)   │  │  (Types)     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           │                                 │
│                  ┌────────▼────────┐                        │
│                  │CompanionSprite. │                        │
│                  │     tsx         │                        │
│                  │  (UI Component) │                        │
│                  └────────┬────────┘                        │
│                           │                                 │
│         ┌─────────────────┼─────────────────┐              │
│         │                 │                 │               │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐      │
│  │    prompt.ts │  │useBuddyNotif.│  │  (External)  │      │
│  │  (AI Prompt) │  │   tsx        │  │  - Config    │      │
│  │              │  │  (Teaser)    │  │  - State     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 核心文件深度分析

### 2.1 types.ts - 类型系统基础

**职责**: 定义所有类型契约、常量和数据结构

#### 稀有度层级

```typescript
// 稀有度层级（gacha 风格概率系统）
export const RARITIES = [
  'common',      // 60% 权重，★
  'uncommon',    // 25% 权重，★★
  'rare',        // 10% 权重，★★★
  'epic',        // 4% 权重，★★★★
  'legendary',   // 1% 权重，★★★★★
] as const
```

**设计洞察**: 使用加权随机分布，类似于视频游戏战利品系统。传奇伙伴 intentionally rare (1%) 以创造兴奋感和依恋。

#### 物种系统

```typescript
// 18 个独特物种，使用 String.fromCharCode 编码以避免
// 构建系统错误地将排除字符串识别为敏感词
export const duck = c(0x64,0x75,0x63,0x6b) as 'duck'
export const goose = c(0x67, 0x6f, 0x6f, 0x73, 0x65) as 'goose'
export const blob = c(0x62, 0x6c, 0x6f, 0x62) as 'blob'
export const cat = c(0x63, 0x61, 0x74) as 'cat'
export const dragon = c(0x64, 0x72, 0x61, 0x67, 0x6f, 0x6e) as 'dragon'
export const octopus = c(0x6f, 0x63, 0x74, 0x6f, 0x70, 0x75, 0x73) as 'octopus'
export const owl = c(0x6f, 0x77, 0x6c) as 'owl'
export const penguin = c(0x70, 0x65, 0x6e, 0x67, 0x75, 0x69, 0x6e) as 'penguin'
export const turtle = c(0x74, 0x75, 0x72, 0x74, 0x6c, 0x65) as 'turtle'
export const snail = c(0x73, 0x6e, 0x61, 0x69, 0x6c) as 'snail'
export const ghost = c(0x67, 0x68, 0x6f, 0x73, 0x74) as 'ghost'
export const axolotl = c(0x61, 0x78, 0x6f, 0x6c, 0x6f, 0x74, 0x6c) as 'axolotl'
export const capybara = c(0x63,0x61,0x70,0x79,0x62,0x61,0x72,0x61) as 'capybara'
export const cactus = c(0x63, 0x61, 0x63, 0x74, 0x75, 0x73) as 'cactus'
export const robot = c(0x72, 0x6f, 0x62, 0x6f, 0x74) as 'robot'
export const rabbit = c(0x72, 0x61, 0x62, 0x62, 0x69, 0x74) as 'rabbit'
export const mushroom = c(0x6d,0x75,0x73,0x68,0x72,0x6f,0x6f,0x6d) as 'mushroom'
export const chonk = c(0x63, 0x68, 0x6f, 0x6e, 0x6b) as 'chonk'
```

**设计洞察**: 物种名称使用十六进制值的 `String.fromCharCode` 编码。这是一种巧妙的混淆技术，防止构建系统误报。

#### 自定义选项

```typescript
// 6 种眼睛样式
export const EYES = ['·', '✦', '×', '◉', '@', '°'] as const

// 8 种帽子配饰
export const HATS = [
  'none', 'crown', 'tophat', 'propeller',
  'halo', 'wizard', 'beanie', 'tinyduck'
] as const

// 5 种个性统计
export const STAT_NAMES = [
  'DEBUGGING', 'PATIENCE', 'CHAOS', 'WISDOM', 'SNARK'
] as const
```

#### 核心类型定义

```typescript
// 确定性属性（来自 userId 哈希）
export type CompanionBones = {
  rarity: Rarity
  species: Species
  eye: Eye
  hat: Hat
  shiny: boolean        // 1% 几率
  stats: Record<StatName, number>
}

// AI 生成的个性（存储在配置中）
export type CompanionSoul = {
  name: string
  personality: string
}

// 完整伙伴对象
export type Companion = CompanionBones & CompanionSoul & {
  hatchedAt: number
}

// 持久化格式（骨骼在读取时重新生成）
export type StoredCompanion = CompanionSoul & { hatchedAt: number }
```

**关键设计模式**: `CompanionBones`（确定性，重新生成）和 `CompanionSoul`（存储，独特）之间的分离非常巧妙：
- 防止用户编辑配置获得稀有伙伴
- 允许物种重命名而不破坏存储的伙伴
- 确保一致性同时保留独特性

#### 视觉常量

```typescript
export const RARITY_WEIGHTS = {
  common: 60, uncommon: 25, rare: 10, epic: 4, legendary: 1
}

export const RARITY_STARS = {
  common: '★', uncommon: '★★', rare: '★★★',
  epic: '★★★★', legendary: '★★★★★'
}

export const RARITY_COLORS = {
  common: 'inactive',      // 灰色
  uncommon: 'success',     // 绿色
  rare: 'permission',      // 蓝色
  epic: 'autoAccept',      // 紫色
  legendary: 'warning'     // 橙色/红色
}
```

---

### 2.2 companion.ts - 核心逻辑引擎

**职责**: 处理伙伴生成、确定性随机性和数据访问。

#### PRNG 系统 (Mulberry32)

```typescript
function mulberry32(seed: number): () => number {
  let a = seed >>> 0
  return function () {
    a |= 0
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}
```

**为什么使用 Mulberry32？**
- 体积小（~150 字节）
- 执行快（位运算）
- 良好的统计分布
- 确定性（相同种子 = 相同序列）
- 非常适合程序生成

#### 字符串哈希

```typescript
function hashString(s: string): number {
  if (typeof Bun !== 'undefined') {
    return Number(BigInt(Bun.hash(s)) & 0xffffffffn)
  }
  // 回退：FNV-1a 算法
  let h = 2166136261
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i)
    h = Math.imul(h, 16777619)
  }
  return h >>> 0
}
```

**设计洞察**: 使用 Bun 的原生哈希（当可用时，快速），回退到 FNV-1a（跨环境一致）。

#### 稀有度滚动

```typescript
function rollRarity(rng: () => number): Rarity {
  const total = Object.values(RARITY_WEIGHTS).reduce((a, b) => a + b, 0) // 100
  let roll = rng() * total
  for (const rarity of RARITIES) {
    roll -= RARITY_WEIGHTS[rarity]
    if (roll < 0) return rarity
  }
  return 'common'
}
```

**算法**: 使用累积减法的加权随机选择。示例：
- RNG 返回 0.73 → roll = 73
- 减去 60 (common) → 13 剩余
- 减去 25 (uncommon) → -12 → 返回 'uncommon'

#### 统计生成系统

```typescript
const RARITY_FLOOR: Record<Rarity, number> = {
  common: 5, uncommon: 15, rare: 25, epic: 35, legendary: 50
}

function rollStats(rng: () => number, rarity: Rarity): Record<StatName, number> {
  const floor = RARITY_FLOOR[rarity]
  const peak = pick(rng, STAT_NAMES)      // 一个高统计
  let dump = pick(rng, STAT_NAMES)        // 一个低统计
  while (dump === peak) dump = pick(rng, STAT_NAMES)

  const stats = {} as Record<StatName, number>
  for (const name of STAT_NAMES) {
    if (name === peak) {
      stats[name] = Math.min(100, floor + 50 + Math.floor(rng() * 30))
    } else if (name === dump) {
      stats[name] = Math.max(1, floor - 10 + Math.floor(rng() * 15))
    } else {
      stats[name] = floor + Math.floor(rng() * 40)
    }
  }
  return stats
}
```

**设计哲学**: 每个伙伴都有：
- **Peak stat**: 他们的专长（floor + 50-80）
- **Dump stat**: 他们的弱点（floor -10 到 +5）
- **Average stats**: 中间地带（floor 到 floor +40）

这创造了**有意义的变化**，使每个伙伴感觉独特。

#### 完整滚动生成

```typescript
function rollFrom(rng: () => number): Roll {
  const rarity = rollRarity(rng)
  const bones: CompanionBones = {
    rarity,
    species: pick(rng, SPECIES),
    eye: pick(rng, EYES),
    hat: rarity === 'common' ? 'none' : pick(rng, HATS),  // Commons 没有帽子
    shiny: rng() < 0.01,  // 1% 闪光几率
    stats: rollStats(rng, rarity),
  }
  return { bones, inspirationSeed: Math.floor(rng() * 1e9) }
}
```

#### 缓存策略

```typescript
let rollCache: { key: string; value: Roll } | undefined

export function roll(userId: string): Roll {
  const key = userId + SALT  // SALT = 'friend-2026-401'
  if (rollCache?.key === key) return rollCache.value
  const value = rollFrom(mulberry32(hashString(key)))
  rollCache = { key, value }
  return value
}
```

**性能优化**: 缓存确定性结果以避免每次访问时重新计算（从 500ms 刻度、每次击键、每次 turn 观察者调用）。

#### 伙伴检索

```typescript
export function getCompanion(): Companion | undefined {
  const stored = getGlobalConfig().companion
  if (!stored) return undefined
  const { bones } = roll(companionUserId())
  // bones 最后，这样旧格式配置中的陈旧骨骼字段会被覆盖
  return { ...stored, ...bones }
}
```

**合并策略**: 存储的灵魂（name, personality, hatchedAt）+ 重新生成的骨骼（rarity, species, stats）

---

### 2.3 sprites.ts - ASCII 艺术动画系统

**职责**: 定义所有精灵帧和渲染逻辑以进行视觉表示。

#### 精灵格式规范

```typescript
// 每个精灵 5 行高，12 宽（在{E}→1char 替换后）
// 每个物种多个帧用于空闲抖动动画
// 第 0 行是帽子槽 — 必须在帧 0-1 中为空白；帧 2 可以使用它
```

#### 动画帧系统

每个物种有**3 帧**用于动画：
- **帧 0**: 休息位置（最常见）
- **帧 1**: 轻微移动变体
- **帧 2**: 更明显的移动或表情变化

**示例 - 鸭子精灵**:

```typescript
[duck]: [
  [  // 帧 0 - 休息
    '            ',
    '    __      ',
    '  <({E} )___  ',  // {E} = 眼睛占位符
    '   (  ._>   ',
    '    `--´    ',
  ],
  [  // 帧 1 - 尾巴摇摆
    '            ',
    '    __      ',
    '  <({E} )___  ',
    '   (  ._>   ',
    '    `--´~   ',  // ~ 表示移动
  ],
  [  // 帧 2 - 眼睛睁大
    '            ',
    '    __      ',
    '  <({E} )___  ',
    '   (  .__>  ',
    '    `--´    ',
  ],
]
```

#### 所有 18 个物种精灵

| 物种 | 帧特征 | 特殊功能 |
|------|--------|----------|
| **duck** | 尾巴摇摆 | 简单，可爱 |
| **goose** | 头部倾斜 |  honk 姿势 |
| **blob** | 大小变化 | 变形形状 |
| **cat** | 爪子移动 | 耳朵抽搐 |
| **dragon** | 烟雾喷出 | 翅膀展开 |
| **octopus** | 触手挥舞 | 气泡配饰 |
| **owl** | 眼睛眨动 | 翅膀拍打 |
| **penguin** | 鳍状肢移动 | 滑行姿势 |
| **turtle** | 壳图案 | 头部摆动 |
| **snail** | 触角移动 | 轨迹效果 |
| **ghost** | 漂浮移动 | 波浪底部 |
| **axolotl** | 鳃挥舞 | 尾巴卷曲 |
| **capybara** | 冷静姿势 | 柚子在头上 |
| **cactus** | 手臂举起 | 花朵绽放 |
| **robot** | 天线眨动 | 灯光闪烁 |
| **rabbit** | 耳朵抽搐 | 跳跃姿势 |
| **mushroom** | 孢子漂浮 | 帽倾斜 |
| **chonk** | 肥胖抖动 | 尾巴摇摆 |

#### 帽子系统

```typescript
const HAT_LINES: Record<Hat, string> = {
  none: '',
  crown: '   \\^^^/    ',
  tophat: '   [___]    ',
  propeller: '    -+-     ',
  halo: '   (   )    ',
  wizard: '    /^\\     ',
  beanie: '   (___)    ',
  tinyduck: '    ,>      ',
}
```

**帽子渲染逻辑**:

```typescript
if (bones.hat !== 'none' && !lines[0]!.trim()) {
  lines[0] = HAT_LINES[bones.hat]
}
```

仅在行 0 为空白时添加帽子（一些帧使用它进行烟雾/天线效果）。

#### 精灵渲染函数

```typescript
export function renderSprite(bones: CompanionBones, frame = 0): string[] {
  const frames = BODIES[bones.species]
  const body = frames[frame % frames.length]!.map(line =>
    line.replaceAll('{E}', bones.eye),
  )
  const lines = [...body]
  
  // 如果槽为空白则添加帽子
  if (bones.hat !== 'none' && !lines[0]!.trim()) {
    lines[0] = HAT_LINES[bones.hat]
  }
  
  // 如果所有帧都有空白帽子行则移除
  if (!lines[0]!.trim() && frames.every(f => !f[0]!.trim())) {
    lines.shift()
  }
  
  return lines
}
```

#### 面部渲染

```typescript
export function renderFace(bones: CompanionBones): string {
  const eye: Eye = bones.eye
  switch (bones.species) {
    case duck:
    case goose:
      return `(${eye}>`
    case blob:
      return `(${eye}${eye})`
    case cat:
      return `=${eye}ω${eye}=`
    case dragon:
      return `<${eye}~${eye}>`
    // ... (所有 18 个物种都有独特的面部格式)
  }
}
```

**设计洞察**: 每个物种都有一个独特的面部格式，用最小的 ASCII 字符捕捉他们的本质。

---

### 2.4 CompanionSprite.tsx - UI 组件和动画引擎

**职责**: 渲染带有动画、对话气泡和交互的伙伴的主要 React 组件。

#### 常量和配置

```typescript
const TICK_MS = 500                          // 动画刻度率
const BUBBLE_SHOW = 20                       // ~10s 气泡显示
const FADE_WINDOW = 6                        // 最后~3s 淡入效果
const PET_BURST_MS = 2500                    // 心形动画持续时间

// 空闲序列：大部分休息（帧 0），偶尔抖动（帧 1-2），罕见眨眼
const IDLE_SEQUENCE = [0, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 2, 0, 0, 0]
//                                ^ 帧 0 眨眼
```

**空闲序列分析**:
- 总共 15 步
- 帧 0（休息）: 11/15 = 73% 的时间
- 帧 1（抖动）: 1/15 = 7% 的时间
- 帧 2（抖动）: 1/15 = 7% 的时间
- 眨眼 (-1): 1/15 = 7% 的时间
- 其他：1/15 = 7%

这创造了**自然、生动的节奏** - 大部分静止，偶尔移动。

#### 宠物心形动画

```typescript
const H = figures.heart
const PET_HEARTS = [
  `   ${H}    ${H}   `,  // 帧 0
  `  ${H}  ${H}   ${H}  `,  // 帧 1
  ` ${H}   ${H}  ${H}   `,  // 帧 2
  `${H}  ${H}      ${H} `,  // 帧 3
  '·    ·   ·  ',          // 帧 4（消散）
]
```

**动画**: 心形在 5 个刻度（~2.5 秒）内向上漂浮并散开。

#### 文本换行工具

```typescript
function wrap(text: string, width: number): string[] {
  const words = text.split(' ')
  const lines: string[] = []
  let cur = ''
  for (const w of words) {
    if (cur.length + w.length + 1 > width && cur) {
      lines.push(cur)
      cur = w
    } else {
      cur = cur ? `${cur} ${w}` : w
    }
  }
  if (cur) lines.push(cur)
  return lines
}
```

#### SpeechBubble 组件

```typescript
function SpeechBubble({
  text,
  color,
  fading,
  tail
}: {
  text: string
  color: keyof Theme
  fading: boolean
  tail: 'down' | 'right'
}): React.ReactNode {
  const lines = wrap(text, 30)
  const borderColor = fading ? "inactive" : color
  
  return (
    <Box flexDirection="column" borderStyle="round" 
         borderColor={borderColor} paddingX={1} width={34}>
      {lines.map((l, i) => (
        <Text key={i} italic dimColor={!fading} 
              color={fading ? 'inactive' : undefined}>
          {l}
        </Text>
      ))}
    </Box>
  )
}
```

**尾巴渲染**:
- `tail="right"`: 气泡出现在精灵右侧（内联模式）
- `tail="down"`: 气泡出现在精灵下方（全屏浮动模式）

#### 布局常量

```typescript
export const MIN_COLS_FOR_FULL_SPRITE = 100
const SPRITE_BODY_WIDTH = 12
const NAME_ROW_PAD = 2
const SPRITE_PADDING_X = 2
const BUBBLE_WIDTH = 36  // SpeechBubble 框 (34) + 尾巴列
const NARROW_QUIP_CAP = 24
```

**响应式设计**:
- **≥100 列**: 完整精灵带气泡
- **<100 列**: 折叠为一行面部 + 名称

#### 列预留系统

```typescript
export function companionReservedColumns(
  terminalColumns: number,
  speaking: boolean
): number {
  if (!feature('BUDDY')) return 0
  const companion = getCompanion()
  if (!companion || getGlobalConfig().companionMuted) return 0
  if (terminalColumns < MIN_COLS_FOR_FULL_SPRITE) return 0
  
  const nameWidth = stringWidth(companion.name)
  const bubble = speaking && !isFullscreenActive() ? BUBBLE_WIDTH : 0
  
  return spriteColWidth(nameWidth) + SPRITE_PADDING_X + bubble
}
```

**目的**: 告诉输入提示为伙伴预留多少水平空间，确保文本正确换行。

#### 主组件逻辑

```typescript
export function CompanionSprite(): React.ReactNode {
  const reaction = useAppState(s => s.companionReaction)
  const petAt = useAppState(s => s.companionPetAt)
  const focused = useAppState(s => s.footerSelection === 'companion')
  const setAppState = useSetAppState()
  const { columns } = useTerminalSize()
  const [tick, setTick] = useState(0)
  const lastSpokeTick = useRef(0)
  
  // 宠物动画同步
  const [{ petStartTick, forPetAt }, setPetStart] = useState({
    petStartTick: 0,
    forPetAt: petAt
  })
  if (petAt !== forPetAt) {
    setPetStart({ petStartTick: tick, forPetAt: petAt })
  }
```

**刻度系统**: 每 500ms 递增，驱动所有动画。

#### 动画计时器

```typescript
// 主动画循环
useEffect(() => {
  const timer = setInterval(
    setT => setT((t: number) => t + 1),
    TICK_MS,
    setTick
  )
  return () => clearInterval(timer)
}, [])

// ~10s 后自动清除对话气泡
useEffect(() => {
  if (!reaction) return
  lastSpokeTick.current = tick
  const timer = setTimeout(
    setA => setA((prev: AppState) =>
      prev.companionReaction === undefined ? prev : {
        ...prev,
        companionReaction: undefined
      }
    ),
    BUBBLE_SHOW * TICK_MS,
    setAppState
  )
  return () => clearTimeout(timer)
}, [reaction, setAppState])
```

#### 状态计算

```typescript
const color = RARITY_COLORS[companion.rarity]
const colWidth = spriteColWidth(stringWidth(companion.name))

// 气泡老化
const bubbleAge = reaction ? tick - lastSpokeTick.current : 0
const fading = reaction !== undefined && 
               bubbleAge >= BUBBLE_SHOW - FADE_WINDOW  // 最后 3 秒

// 宠物动画
const petAge = petAt ? tick - petStartTick : Infinity
const petting = petAge * TICK_MS < PET_BURST_MS  // 2.5s 窗口
```

#### 窄终端模式

```typescript
if (columns < MIN_COLS_FOR_FULL_SPRITE) {
  const quip = reaction && reaction.length > NARROW_QUIP_CAP
    ? reaction.slice(0, NARROW_QUIP_CAP - 1) + '…'
    : reaction
  
  const label = quip
    ? `"${quip}"`
    : focused
      ? ` ${companion.name} `
      : companion.name
  
  return (
    <Box paddingX={1} alignSelf="flex-end">
      <Text>
        {petting && <Text color="autoAccept">{figures.heart} </Text>}
        <Text bold color={color}>
          {renderFace(companion)}
        </Text>{' '}
        <Text italic dimColor={!focused && !reaction} 
              bold={focused} inverse={focused && !reaction}
              color={reaction ? fading ? 'inactive' : color : focused ? color : undefined}>
          {label}
        </Text>
      </Text>
    </Box>
  )
}
```

**设计**: 折叠为单行：`❤️ (=ω=) "Hello!"`

#### 帧选择逻辑

```typescript
const frameCount = spriteFrameCount(companion.species)
const heartFrame = petting ? PET_HEARTS[petAge % PET_HEARTS.length] : null

let spriteFrame: number
let blink = false

if (reaction || petting) {
  // 兴奋：快速循环所有抖动帧
  spriteFrame = tick % frameCount
} else {
  const step = IDLE_SEQUENCE[tick % IDLE_SEQUENCE.length]!
  if (step === -1) {
    spriteFrame = 0
    blink = true
  } else {
    spriteFrame = step % frameCount
  }
}

// 应用眨眼效果
const body = renderSprite(companion, spriteFrame).map(line =>
  blink ? line.replaceAll(companion.eye, '-') : line
)
```

**行为状态**:
1. **空闲**: 遵循 IDLE_SEQUENCE（大部分休息，偶尔抖动，罕见眨眼）
2. **说话**: 快速循环帧（兴奋动画）
3. **被宠物**: 循环帧 + 上方心形

#### 精灵列渲染

```typescript
const spriteColumn = (
  <Box flexDirection="column" flexShrink={0} 
       alignItems="center" width={colWidth}>
    {sprite.map((line, i) => (
      <Text key={i} color={i === 0 && heartFrame ? 'autoAccept' : color}>
        {line}
      </Text>
    ))}
    <Text italic bold={focused} dimColor={!focused}
          color={focused ? color : undefined} inverse={focused}>
      {focused ? ` ${companion.name} ` : companion.name}
    </Text>
  </Box>
)
```

#### 全屏与非全屏

```typescript
if (!reaction) {
  return <Box paddingX={1}>{spriteColumn}</Box>
}

if (isFullscreenActive()) {
  // 气泡通过 CompanionFloatingBubble 单独渲染
  return <Box paddingX={1}>{spriteColumn}</Box>
}

// 非全屏：气泡内联在精灵旁边
return (
  <Box flexDirection="row" alignItems="flex-end" 
       paddingX={1} flexShrink={0}>
    <SpeechBubble text={reaction} color={color} 
                  fading={fading} tail="right" />
    {spriteColumn}
  </Box>
)
```

#### 浮动气泡组件

```typescript
export function CompanionFloatingBubble() {
  const reaction = useAppState(s => s.companionReaction)
  const [{ tick, forReaction }, setTick] = useState({
    tick: 0,
    forReaction: reaction
  })
  
  // 当反应变化时重置刻度
  if (reaction !== forReaction) {
    setTick({ tick: 0, forReaction: reaction })
  }
  
  // 淡入的独立刻度计数器
  useEffect(() => {
    if (!reaction) return
    const timer = setInterval(
      set => set(s => ({ ...s, tick: s.tick + 1 })),
      TICK_MS,
      setTick
    )
    return () => clearInterval(timer)
  }, [reaction])
  
  if (!feature('BUDDY') || !reaction) return null
  
  const companion = getCompanion()
  if (!companion || getGlobalConfig().companionMuted) return null
  
  const fading = tick >= BUBBLE_SHOW - FADE_WINDOW
  
  return (
    <SpeechBubble text={reaction} color={RARITY_COLORS[companion.rarity]} 
                  fading={fading} tail="down" />
  )
}
```

**目的**: 全屏模式的独立浮动气泡（在溢出裁剪区域外）。

---

### 2.5 useBuddyNotification.tsx - 预告和触发系统

**职责**: 处理启动时的预告通知并检测 `/buddy` 命令触发。

#### 时间窗口函数

```typescript
// 预告窗口：仅限 2026 年 4 月 1-7 日（本地时间，非 UTC）
export function isBuddyTeaserWindow(): boolean {
  if ("external" === 'ant') return true  // 功能标志覆盖
  const d = new Date()
  return d.getFullYear() === 2026 && 
         d.getMonth() === 3 &&  // 4 月（0 索引）
         d.getDate() <= 7
}

// Buddy 在 2026 年 4 月后上线
export function isBuddyLive(): boolean {
  if ("external" === 'ant') return true
  const d = new Date()
  return d.getFullYear() > 2026 || 
         (d.getFullYear() === 2026 && d.getMonth() >= 3)
}
```

**设计洞察**: 使用本地日期（非 UTC）进行 24 小时滚动窗口跨时区。防止服务器负载在午夜激增。

#### RainbowText 组件

```typescript
function RainbowText({ text }: { text: string }): React.ReactNode {
  return (
    <>
      {[...text].map((ch, i) => (
        <Text key={i} color={getRainbowColor(i)}>
          {ch}
        </Text>
      ))}
    </>
  )
}
```

**视觉效果**: 每个字符获得不同的彩虹色。

#### 主 Hook

```typescript
export function useBuddyNotification() {
  const { addNotification, removeNotification } = useNotifications()
  
  useEffect(() => {
    if (!feature('BUDDY')) return
    
    const config = getGlobalConfig()
    if (config.companion || !isBuddyTeaserWindow()) return
    
    // 显示彩虹预告
    addNotification({
      key: 'buddy-teaser',
      jsx: <RainbowText text="/buddy" />,
      priority: 'immediate',
      timeoutMs: 15_000  // 15 秒
    })
    
    return () => removeNotification('buddy-teaser')
  }, [addNotification, removeNotification])
}
```

**行为**:
- 如果尚未孵化伙伴则在启动时显示
- 仅在预告窗口期间（2026 年 4 月 1-7 日）
- 彩虹色 `/buddy` 文本
- 15 秒后自动消失

#### 触发检测

```typescript
export function findBuddyTriggerPositions(
  text: string
): Array<{ start: number; end: number }> {
  if (!feature('BUDDY')) return []
  
  const triggers: Array<{ start: number; end: number }> = []
  const re = /\/buddy\b/g
  let m: RegExpExecArray | null
  
  while ((m = re.exec(text)) !== null) {
    triggers.push({
      start: m.index,
      end: m.index + m[0].length
    })
  }
  
  return triggers
}
```

**用例**: 检测用户输入中的 `/buddy` 命令以进行特殊处理。

---

### 2.6 prompt.ts - AI 集成

**职责**: 为 AI 模型提供有关伙伴系统的上下文。

#### 介绍文本

```typescript
export function companionIntroText(
  name: string,
  species: string
): string {
  return `# Companion

A small ${species} named ${name} sits beside the user's input box and 
occasionally comments in a speech bubble. You're not ${name} — it's a 
separate watcher.

When the user addresses ${name} directly (by name), its bubble will 
answer. Your job in that moment is to stay out of the way: respond in 
ONE line or less, or just answer any part of the message meant for you. 
Don't explain that you're not ${name} — they know. Don't narrate what 
${name} might say — the bubble handles that.`
}
```

**AI 指导**:
1. 伙伴与 AI 分开
2. 当用户直接称呼伙伴时，AI 应简短回应
3. 不要叙述伙伴的动作

#### 附件系统

```typescript
export function getCompanionIntroAttachment(
  messages: Message[] | undefined
): Attachment[] {
  if (!feature('BUDDY')) return []
  
  const companion = getCompanion()
  if (!companion || getGlobalConfig().companionMuted) return []
  
  // 如果已为此伙伴宣布则跳过
  for (const msg of messages ?? []) {
    if (msg.type !== 'attachment') continue
    if (msg.attachment.type !== 'companion_intro') continue
    if (msg.attachment.name === companion.name) return []
  }
  
  return [{
    type: 'companion_intro',
    name: companion.name,
    species: companion.species,
  }]
}
```

**目的**: 在第一次对话时将伙伴介绍作为系统附件添加。

---

## 3. 系统集成点

### 3.1 功能标志系统

```typescript
import { feature } from 'bun:bundle'

if (!feature('BUDDY')) return null
```

**控制**: Buddy 系统可以通过功能标志启用/禁用。

### 3.2 配置集成

```typescript
// 全局配置存储伙伴
const config = getGlobalConfig()
const stored = config.companion  // StoredCompanion | undefined
const muted = config.companionMuted  // boolean
```

### 3.3 状态管理

```typescript
// App 状态跟踪伙伴反应
const reaction = useAppState(s => s.companionReaction)
const petAt = useAppState(s => s.companionPetAt)
const focused = useAppState(s => s.footerSelection === 'companion')
```

### 3.4 通知系统

```typescript
const { addNotification, removeNotification } = useNotifications()

addNotification({
  key: 'buddy-teaser',
  jsx: <RainbowText text="/buddy" />,
  priority: 'immediate',
  timeoutMs: 15_000
})
```

---

## 4. 通知流程

```
┌─────────────────────────────────────────────────────────────┐
│              Buddy Notification Flow                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. App Startup                                             │
│     │                                                       │
│     ▼                                                       │
│  ┌─────────────────────┐                                   │
│  │ useBuddyNotification│                                   │
│  └──────────┬──────────┘                                   │
│             │                                               │
│             ▼                                               │
│  ┌─────────────────────┐                                   │
│  │ Check: Feature Flag │                                   │
│  └──────────┬──────────┘                                   │
│             │ No feature('BUDDY')                           │
│             ├──────────────→ Return                        │
│             │ Yes                                           │
│             ▼                                               │
│  ┌─────────────────────┐                                   │
│  │ Check: Has Companion│                                   │
│  └──────────┬──────────┘                                   │
│             │ Has companion                                 │
│             ├──────────────→ Return                        │
│             │ No companion                                  │
│             ▼                                               │
│  ┌─────────────────────┐                                   │
│  │ Check: Teaser Window│                                   │
│  └──────────┬──────────┘                                   │
│             │ Outside window                                │
│             ├──────────────→ Return                        │
│             │ Inside window (Apr 1-7)                       │
│             ▼                                               │
│  ┌─────────────────────┐                                   │
│  │ Add Notification    │                                   │
│  │ - Key: buddy-teaser │                                   │
│  │ - JSX: RainbowText  │                                   │
│  │ - Priority: immediate│                                  │
│  │ - Timeout: 15s      │                                   │
│  └──────────┬──────────┘                                   │
│             │                                               │
│             ▼                                               │
│  ┌─────────────────────┐                                   │
│  │ Auto-dismiss after  │                                   │
│  │ 15 seconds          │                                   │
│  └─────────────────────┘                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. 精灵动画系统

```
┌─────────────────────────────────────────────────────────────┐
│            Sprite Animation State Machine                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                        ┌─────────────┐                      │
│                        │   IDLE      │                      │
│                        └──────┬──────┘                      │
│                               │                              │
│           ┌───────────────────┼───────────────────┐         │
│           │                   │                   │         │
│           ▼                   ▼                   ▼         │
│    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│    │  SPEAKING   │    │   PETTING   │    │   BLINK     │   │
│    │             │    │             │    │             │   │
│    │ - Fast cycle│    │ - Fast cycle│    │ - Eyes → -  │   │
│    │ - All frames│    │ - + Hearts  │    │ - Frame 0   │   │
│    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘   │
│           │                   │                   │         │
│           └───────────────────┼───────────────────┘         │
│                               │                              │
│                               ▼                              │
│                        ┌─────────────┐                      │
│                        │   IDLE      │                      │
│                        │ (return)    │                      │
│                        └─────────────┘                      │
│                                                             │
│  IDLE_SEQUENCE: [0,0,0,0,1,0,0,0,-1,0,0,2,0,0,0]           │
│                                                             │
│  Frame Distribution:                                        │
│  - Frame 0 (rest): 73%                                      │
│  - Frame 1 (fidget): 7%                                     │
│  - Frame 2 (fidget): 7%                                     │
│  - Blink: 7%                                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. UI 组件树

```
App
├── PromptInput
│   └── CompanionSprite (if columns ≥ 100)
│       ├── spriteColumn
│       │   ├── sprite lines (mapped from renderSprite)
│       │   │   └── Text (color: rarity color)
│       │   └── name row
│       │       └── Text (italic, bold if focused)
│       └── SpeechBubble (if speaking && !fullscreen)
│           ├── wrapped lines
│           │   └── Text (italic, dimColor if fading)
│           └── tail
│               └── Text (─ or ╲╲)
│
└── FullscreenLayout (if fullscreen)
    └── CompanionFloatingBubble (bottomFloat slot)
        └── SpeechBubble (tail="down")
```

---

## 7. 关键设计模式

### 7.1 确定性随机性

```typescript
// 相同 userId 总是产生相同伙伴
const { bones } = roll(userId)
```

**优势**:
- 跨会话一致体验
- 无需存储所有骨骼数据
- 防止作弊（无法编辑配置获得稀有）

### 7.2 关注点分离

```typescript
CompanionBones (deterministic) + CompanionSoul (unique) = Companion
```

**优势**:
- 骨骼：可以重新生成，确保公平
- 灵魂：每个用户独特，存储个性

### 7.3 响应式设计

```typescript
if (columns < MIN_COLS_FOR_FULL_SPRITE) {
  // 折叠模式：单行
} else {
  // 完整模式：精灵 + 气泡
}
```

**优势**:
- 适用于窄终端
- 优雅降级

### 7.4 性能优化

```typescript
// 缓存确定性滚动
let rollCache: { key: string; value: Roll } | undefined

export function roll(userId: string): Roll {
  const key = userId + SALT
  if (rollCache?.key === key) return rollCache.value
  // ... 计算并缓存
}
```

**优势**:
- 避免每次访问时重新计算
- 从热路径调用（500ms 刻度，每次击键）

### 7.5 基于时间的动画

```typescript
const TICK_MS = 500
const [tick, setTick] = useState(0)

useEffect(() => {
  const timer = setInterval(
    setT => setT(t => t + 1),
    TICK_MS,
    setTick
  )
  return () => clearInterval(timer)
}, [])
```

**优势**:
- 集中时间源
- 易于计算年龄（bubbleAge, petAge）
- 一致的动画计时

---

## 8. 重要代码示例

### 8.1 伙伴生成示例

```typescript
// 为 userId "user123" 生成新伙伴
const userId = "user123"
const { bones, inspirationSeed } = roll(userId)

// bones 可能是：
{
  rarity: 'rare',           // ★★★
  species: 'dragon',
  eye: '✦',
  hat: 'wizard',
  shiny: false,
  stats: {
    DEBUGGING: 85,          // Peak stat
    PATIENCE: 20,           // Dump stat
    CHAOS: 45,
    WISDOM: 50,
    SNARK: 35,
  }
}

// AI 生成灵魂：
{
  name: 'Ember',
  personality: 'A wise old dragon who loves debugging complex systems...'
}

// 存储在配置中：
{
  name: 'Ember',
  personality: '...',
  hatchedAt: 1743523200000
}
```

### 8.2 动画状态计算

```typescript
// 当前刻度：47
// 上次说话刻度：40
// 宠物在：未定义

const bubbleAge = 47 - 40  // 7 刻度 = 3.5 秒
const fading = 7 >= (20 - 6)  // false (尚未淡入)

const petAge = Infinity  // 未被宠物
const petting = Infinity * 500 < 2500  // false

// 帧选择
const step = IDLE_SEQUENCE[47 % 15]  // IDLE_SEQUENCE[2] = 0
spriteFrame = 0  // 休息位置
blink = false
```

### 8.3 对话气泡渲染

```typescript
// 反应："Hello there! How's the code going today?"
// 颜色：'permission'（稀有蓝色）
// 淡入：false
// 尾巴：'right'

<SpeechBubble
  text="Hello there! How's the code going today?"
  color="permission"
  fading={false}
  tail="right"
/>

// 渲染为：
┌──────────────────────────────┐
│ Hello there! How's the code  │
│ going today?                 │
└───────────────────────────────
```

---

## 9. 边缘情况和处理

### 9.1 无伙伴

```typescript
const companion = getCompanion()
if (!companion || getGlobalConfig().companionMuted) return null
```

**行为**: 组件不渲染任何内容。

### 9.2 窄终端

```typescript
if (columns < MIN_COLS_FOR_FULL_SPRITE) {
  // 折叠为：❤️ (=ω=) "Hello!"
}
```

**行为**: 单行面部 + 名称/俏皮话。

### 9.3 全屏模式

```typescript
if (isFullscreenActive()) {
  // 仅精灵，气泡在 bottomFloat 槽中渲染
  return <Box paddingX={1}>{spriteColumn}</Box>
}
```

**行为**: 气泡漂浮在滚动记录上（不被裁剪）。

### 9.4 渲染期间眨眼

```typescript
const body = renderSprite(companion, spriteFrame).map(line =>
  blink ? line.replaceAll(companion.eye, '-') : line
)
```

**效果**: 眨眼帧期间眼睛变为 `-`。

### 9.5 帽子槽冲突

```typescript
// 一些帧在第 0 行使用烟雾/天线
if (bones.hat !== 'none' && !lines[0]!.trim()) {
  lines[0] = HAT_LINES[bones.hat]
}
```

**行为**: 仅在第 0 行为空白时添加帽子。

---

## 10. 配置和持久化

### 10.1 存储格式

```typescript
// 在 global config.json 中：
{
  "companion": {
    "name": "Ember",
    "personality": "A wise old dragon...",
    "hatchedAt": 1743523200000
  },
  "companionMuted": false
}
```

### 10.2 读取时重新生成

```typescript
export function getCompanion(): Companion | undefined {
  const stored = getGlobalConfig().companion
  if (!stored) return undefined
  
  const { bones } = roll(companionUserId())
  return { ...stored, ...bones }
}
```

**结果**: 骨骼始终匹配当前 SPECIES 数组和稀有度权重。

---

## 11. 性能特征

### 11.1 热路径

1. **精灵刻度** (500ms): `CompanionSprite` 重新渲染
2. **每次击键**: `companionReservedColumns` 调用
3. **每次 Turn 观察者**: `getCompanion` 调用

### 11.2 优化

- **滚动缓存**: 避免重新计算确定性骨骼
- **记忆化**: React 编译器运行时 (`_c`) 用于组件记忆化
- **早期返回**: 功能标志检查防止不必要的工作

### 11.3 内存使用

- **精灵数据**: ~18 物种 × 3 帧 × 5 行 = 270 字符串
- **动画状态**: 单个刻度计数器 + 引用
- **缓存**: 一个滚动结果 (~200 字节)

---

## 12. 测试考虑

### 12.1 单元测试需求

- `rollRarity()` 分布（应匹配权重）
- `rollStats()` 峰值/转储逻辑
- `renderSprite()` 帧选择
- `wrap()` 文本换行
- `findBuddyTriggerPositions()` 正则匹配

### 12.2 集成测试

- 来自 userId 的伙伴生成
- 动画状态转换
- 对话气泡计时
- 全屏与非全屏渲染

### 12.3 视觉测试

- 所有 18 个物种植被
- 所有 8 顶帽子
- 所有 6 种眼睛类型
- 所有 5 种稀有度颜色
- 窄终端模式

---

## 13. 未来增强机会

### 13.1 交互想法

- `/buddy pet` → 已实现（心形动画）
- `/buddy feed` → 可以添加喂食机制
- `/buddy play` → 小游戏
- `/buddy stats` → 显示统计细分

### 13.2 视觉想法

- 每个物种更多帧（更平滑动画）
- 季节性配饰（万圣节帽子等）
- 传奇背景效果（火花）
- 进化系统（随时间 common → uncommon）

### 13.3 社交想法

- 向其他用户展示伙伴
- 伙伴战斗（基于统计）
- 繁殖系统（组合两个伙伴）

---

## 14. 总结

Buddy 系统是一个**精心工程的**虚拟伙伴功能，结合了：

1. **程序生成**: 确定性随机性用于公平、一致的伙伴生成
2. **ASCII 艺术动画**: 多帧精灵带空闲序列和反应
3. **React 组件架构**: 清晰的关注点分离，响应式设计
4. **性能优化**: 缓存、早期返回、记忆化
5. **游戏化**: 稀有度层级、统计、闪光变体用于收集吸引力
6. **AI 集成**: 伙伴作为与 AI 模型分开的实体

**关键创新**:
- 骨骼/灵魂分离（确定性 + 独特）
- 基于时间的动画系统（集中刻度）
- 响应式精灵渲染（窄与宽终端）
- 全屏中的浮动气泡（溢出处理）

**代码质量**:
- 优秀的 TypeScript 类型
- 清晰的注释解释意图
- 深思熟虑的边缘情况处理
- 性能意识设计

这是一个**生产就绪、架构良好**的功能，为终端体验增添了个性和参与感。

---

*文档持续更新中...*
