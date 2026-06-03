# Full File Catalog (Gap Fill)

> Behavior-level stubs for 1512 files not covered by `###` headings elsewhere.

### `QueryEngine.ts` (1295 lines)

**Exports:**
- `QueryEngineConfig`
- `QueryEngine`

**Dependencies:** `bun:bundle`, `@anthropic-ai/sdk/resources/messages.mjs`, `crypto`, `lodash-es/last`, `src/services/api/claude`, `src/services/api/logging`, `strip-ansi`, `./commands`

**Feature gates:** `COORDINATOR_MODE`, `HISTORY_SNIP`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `Task.ts` (125 lines)

**Exports:**
- `TaskType`
- `TaskStatus`
- `isTerminalTaskStatus()`
- `TaskHandle`
- `SetAppState`
- `TaskContext`
- `TaskStateBase`
- `LocalShellSpawnInput`
- `Task`
- `generateTaskId()`
- `createTaskStateBase()`

**Dependencies:** `crypto`, `./state/AppState`, `./types/ids`, `./utils/task/diskOutput`

**Main flow:** Entry: `isTerminalTaskStatus()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `Tool.ts` (792 lines)

**Exports:**
- `ToolInputJSONSchema`
- `QueryChainTracking`
- `ValidationResult`
- `SetToolJSXFn`
- `ToolPermissionContext`
- `getEmptyToolPermissionContext`
- `CompactProgressEvent`
- `ToolUseContext`
- `Progress`
- `ToolProgress`
- `filterToolProgressMessages()`
- `ToolResult`
- `ToolCallProgress`
- `AnyObject`
- `toolMatchesName()`
- `findToolByName()`
- `Tool`
- `Tools`
- `ToolDef`
- `buildTool()`

**Dependencies:** `crypto`, `zod/v4`, `./commands`, `./hooks/useCanUseTool`, `./utils/thinking`, `./context/notifications`

**Main flow:** Entry: `filterToolProgressMessages()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `assistant/sessionHistory.ts` (87 lines)

**Exports:**
- `HISTORY_PAGE_SIZE`
- `HistoryPage`
- `HistoryAuthCtx`
- `createHistoryAuthCtx()`
- `fetchLatestEvents()`
- `fetchOlderEvents()`

**Dependencies:** `axios`, `../constants/oauth`, `../entrypoints/agentSdkTypes`, `../utils/debug`, `../utils/teleport/api`

**Main flow:** Entry: `createHistoryAuthCtx()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/bridgeApi.ts` (539 lines)

**Exports:**
- `validateBridgeId()`
- `BridgeFatalError`
- `createBridgeApiClient()`
- `isExpiredErrorType()`
- `isSuppressible403()`

**Dependencies:** `axios`, `./debugUtils`

**Main flow:** Entry: `validateBridgeId()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/bridgeConfig.ts` (48 lines)

**Exports:**
- `getBridgeTokenOverride()`
- `getBridgeBaseUrlOverride()`
- `getBridgeAccessToken()`
- `getBridgeBaseUrl()`

**Dependencies:** `../constants/oauth`, `../utils/auth`

**Main flow:** Entry: `getBridgeTokenOverride()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/bridgeDebug.ts` (135 lines)

**Exports:**
- `BridgeDebugHandle`
- `registerBridgeDebugHandle()`
- `clearBridgeDebugHandle()`
- `getBridgeDebugHandle()`
- `injectBridgeFault()`
- `wrapApiForFaultInjection()`

**Dependencies:** `../utils/debug`, `./bridgeApi`, `./types`

**Main flow:** Entry: `registerBridgeDebugHandle()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/bridgeEnabled.ts` (202 lines)

**Exports:**
- `isBridgeEnabled()`
- `isBridgeEnabledBlocking()`
- `getBridgeDisabledReason()`
- `isEnvLessBridgeEnabled()`
- `isCseShimEnabled()`
- `checkBridgeMinVersion()`
- `getCcrAutoConnectDefault()`
- `isCcrMirrorEnabled()`

**Dependencies:** `bun:bundle`, `../utils/auth`, `../utils/envUtils`, `../utils/semver`

**Feature gates:** `BRIDGE_MODE`, `CCR_AUTO_CONNECT`, `CCR_MIRROR`

**Main flow:** Entry: `isBridgeEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/bridgeMain.ts` (2999 lines)

**Exports:**
- `BackoffConfig`
- `runBridgeLoop()`
- `isConnectionError()`
- `isServerError()`
- `ParsedArgs`
- `parseArgs()`
- `bridgeMain()`
- `BridgeHeadlessPermanentError`
- `HeadlessBridgeOpts`
- `runBridgeHeadless()`

**Dependencies:** `bun:bundle`, `crypto`, `os`, `path`, `../constants/product`, `../services/analytics/datadog`, `../services/analytics/firstPartyEventLogger`, `../services/analytics/growthbook`, `../utils/bundledMode`, `../utils/debug`

**Feature gates:** `KAIROS`

**Main flow:** Entry: `runBridgeLoop()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/bridgeMessaging.ts` (461 lines)

**Exports:**
- `isSDKMessage()`
- `isSDKControlResponse()`
- `isSDKControlRequest()`
- `isEligibleBridgeMessage()`
- `extractTitleText()`
- `handleIngressMessage()`
- `ServerControlRequestHandlers`
- `handleServerControlRequest()`
- `makeResultMessage()`
- `BoundedUUIDSet`

**Dependencies:** `crypto`, `../entrypoints/agentSdkTypes`, `../entrypoints/sdk/coreTypes`, `../services/analytics/index`, `../services/api/emptyUsage`, `../types/message`, `../utils/controlMessageCompat`, `../utils/debug`, `../utils/displayTags`, `../utils/errors`

**Main flow:** Entry: `isSDKMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/bridgePermissionCallbacks.ts` (43 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../utils/permissions/PermissionUpdateSchema`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/bridgePointer.ts` (210 lines)

**Exports:**
- `BRIDGE_POINTER_TTL_MS`
- `BridgePointer`
- `getBridgePointerPath()`
- `writeBridgePointer()`
- `readBridgePointer()`
- `readBridgePointerAcrossWorktrees()`
- `clearBridgePointer()`

**Dependencies:** `fs/promises`, `path`, `zod/v4`, `../utils/debug`, `../utils/errors`, `../utils/getWorktreePathsPortable`, `../utils/lazySchema`, `../utils/slowOperations`

**Main flow:** Entry: `getBridgePointerPath()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/bridgeStatusUtil.ts` (163 lines)

**Exports:**
- `StatusState`
- `TOOL_DISPLAY_EXPIRY_MS`
- `SHIMMER_INTERVAL_MS`
- `timestamp()`
- `abbreviateActivity()`
- `buildBridgeConnectUrl()`
- `buildBridgeSessionUrl()`
- `computeGlimmerIndex()`
- `computeShimmerSegments()`
- `BridgeStatusInfo`
- `getBridgeStatus()`
- `buildIdleFooterText()`
- `buildActiveFooterText()`
- `FAILED_FOOTER_TEXT`
- `wrapWithOsc8Link()`

**Dependencies:** `../ink/stringWidth`, `../utils/format`, `../utils/intl`

**Main flow:** Entry: `timestamp()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/bridgeUI.ts` (530 lines)

**Exports:**
- `createBridgeLogger()`

**Dependencies:** `chalk`, `qrcode`, `../ink/stringWidth`, `../utils/debug`

**Main flow:** Entry: `createBridgeLogger()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/capacityWake.ts` (56 lines)

**Exports:**
- `CapacitySignal`
- `CapacityWake`
- `createCapacityWake()`

**Dependencies:** local only

**Main flow:** Entry: `createCapacityWake()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/codeSessionApi.ts` (168 lines)

**Exports:**
- `createCodeSession()`
- `RemoteCredentials`
- `fetchRemoteCredentials()`

**Dependencies:** `axios`, `../utils/debug`, `../utils/errors`, `../utils/slowOperations`, `./debugUtils`

**Main flow:** Entry: `createCodeSession()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/createSession.ts` (384 lines)

**Exports:**
- `createBridgeSession()`
- `getBridgeSession()`
- `archiveBridgeSession()`
- `updateBridgeSessionTitle()`

**Dependencies:** `../entrypoints/agentSdkTypes`, `../utils/debug`, `../utils/errors`, `./debugUtils`, `./sessionIdCompat`

**Main flow:** Entry: `createBridgeSession()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/debugUtils.ts` (141 lines)

**Exports:**
- `redactSecrets()`
- `debugTruncate()`
- `debugBody()`
- `describeAxiosError()`
- `extractHttpStatus()`
- `extractErrorDetail()`
- `logBridgeSkip()`

**Dependencies:** `../utils/debug`, `../utils/errors`, `../utils/slowOperations`

**Main flow:** Entry: `redactSecrets()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/envLessBridgeConfig.ts` (165 lines)

**Exports:**
- `EnvLessBridgeConfig`
- `DEFAULT_ENV_LESS_BRIDGE_CONFIG`
- `getEnvLessBridgeConfig()`
- `checkEnvLessBridgeMinVersion()`
- `shouldShowAppUpgradeMessage()`

**Dependencies:** `zod/v4`, `../services/analytics/growthbook`, `../utils/lazySchema`, `../utils/semver`, `./bridgeEnabled`

**Main flow:** Entry: `getEnvLessBridgeConfig()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/flushGate.ts` (71 lines)

**Exports:**
- `FlushGate`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/inboundAttachments.ts` (175 lines)

**Exports:**
- `InboundAttachment`
- `extractInboundAttachments()`
- `resolveInboundAttachments()`
- `prependPathRefs()`
- `resolveAndPrepend()`

**Dependencies:** `@anthropic-ai/sdk/resources/messages.mjs`, `axios`, `crypto`, `fs/promises`, `path`, `zod/v4`, `../bootstrap/state`, `../utils/debug`, `../utils/envUtils`, `../utils/lazySchema`

**Main flow:** Entry: `extractInboundAttachments()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/inboundMessages.ts` (80 lines)

**Exports:**
- `extractInboundMessageFields()`
- `normalizeImageBlocks()`

**Dependencies:** `crypto`, `../entrypoints/agentSdkTypes`, `../utils/imageResizer`

**Main flow:** Entry: `extractInboundMessageFields()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/initReplBridge.ts` (569 lines)

**Exports:**
- `InitBridgeOptions`
- `initReplBridge()`

**Dependencies:** `bun:bundle`, `os`, `../bootstrap/state`, `../entrypoints/agentSdkTypes`, `../entrypoints/sdk/controlTypes`, `../services/analytics/growthbook`, `../services/oauth/client`, `../types/message`, `../utils/config`, `../utils/debug`

**Feature gates:** `KAIROS`

**Main flow:** Entry: `initReplBridge()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/jwtUtils.ts` (256 lines)

**Exports:**
- `decodeJwtPayload()`
- `decodeJwtExpiry()`
- `createTokenRefreshScheduler()`

**Dependencies:** `../services/analytics/index`, `../utils/debug`, `../utils/diagLogs`, `../utils/errors`, `../utils/slowOperations`

**Main flow:** Entry: `decodeJwtPayload()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/pollConfig.ts` (110 lines)

**Exports:**
- `getPollIntervalConfig()`

**Dependencies:** `zod/v4`, `../services/analytics/growthbook`, `../utils/lazySchema`

**Main flow:** Entry: `getPollIntervalConfig()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/pollConfigDefaults.ts` (82 lines)

**Exports:**
- `PollIntervalConfig`
- `DEFAULT_POLL_CONFIG`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/remoteBridgeCore.ts` (1008 lines)

**Exports:**
- `EnvLessBridgeParams`
- `initEnvLessBridgeCore()`
- `fetchRemoteCredentials()`

**Dependencies:** `bun:bundle`, `axios`, `./workSecret`, `./sessionIdCompat`, `./flushGate`, `./jwtUtils`, `./trustedDevice`

**Feature gates:** `CCR_MIRROR`

**Main flow:** Entry: `initEnvLessBridgeCore()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/replBridge.ts` (2406 lines)

**Exports:**
- `ReplBridgeHandle`
- `BridgeState`
- `BridgeCoreParams`
- `BridgeCoreHandle`
- `initBridgeCore()`

**Dependencies:** `crypto`, `./types`, `../utils/debug`, `../utils/diagLogs`, `../utils/cleanupRegistry`, `./sessionIdCompat`, `../utils/concurrentSessions`, `./trustedDevice`, `../cli/transports/HybridTransport`, `../utils/sessionIngressAuth`

**Main flow:** Entry: `initBridgeCore()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/replBridgeHandle.ts` (36 lines)

**Exports:**
- `setReplBridgeHandle()`
- `getReplBridgeHandle()`
- `getSelfBridgeCompatId()`

**Dependencies:** `../utils/concurrentSessions`, `./replBridge`, `./sessionIdCompat`

**Main flow:** Entry: `setReplBridgeHandle()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/replBridgeTransport.ts` (370 lines)

**Exports:**
- `ReplBridgeTransport`
- `createV1ReplTransport()`
- `createV2ReplTransport()`

**Dependencies:** `src/entrypoints/sdk/controlTypes`, `../cli/transports/ccrClient`, `../cli/transports/HybridTransport`, `../cli/transports/SSETransport`, `../utils/debug`, `../utils/errors`, `../utils/sessionIngressAuth`, `../utils/sessionState`, `./workSecret`

**Main flow:** Entry: `createV1ReplTransport()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/sessionIdCompat.ts` (57 lines)

**Exports:**
- `setCseShimGate()`
- `toCompatSessionId()`
- `toInfraSessionId()`

**Dependencies:** local only

**Main flow:** Entry: `setCseShimGate()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/sessionRunner.ts` (550 lines)

**Exports:**
- `safeFilenameId()`
- `PermissionRequest`
- `createSessionSpawner()`

**Dependencies:** `child_process`, `fs`, `os`, `path`, `readline`, `../utils/slowOperations`, `./debugUtils`

**Main flow:** Entry: `safeFilenameId()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/trustedDevice.ts` (210 lines)

**Exports:**
- `getTrustedDeviceToken()`
- `clearTrustedDeviceTokenCache()`
- `clearTrustedDeviceToken()`
- `enrollTrustedDevice()`

**Dependencies:** `axios`, `lodash-es/memoize`, `os`, `../constants/oauth`, `../utils/debug`, `../utils/errors`, `../utils/privacyLevel`, `../utils/secureStorage/index`, `../utils/slowOperations`

**Main flow:** Entry: `getTrustedDeviceToken()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/types.ts` (262 lines)

**Exports:**
- `DEFAULT_SESSION_TIMEOUT_MS`
- `BRIDGE_LOGIN_INSTRUCTION`
- `BRIDGE_LOGIN_ERROR`
- `REMOTE_CONTROL_DISCONNECTED_MSG`
- `WorkData`
- `WorkResponse`
- `WorkSecret`
- `SessionDoneStatus`
- `SessionActivityType`
- `SessionActivity`
- `SpawnMode`
- `BridgeWorkerType`
- `BridgeConfig`
- `PermissionResponseEvent`
- `BridgeApiClient`
- `SessionHandle`
- `SessionSpawnOpts`
- `SessionSpawner`
- `BridgeLogger`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `bridge/workSecret.ts` (127 lines)

**Exports:**
- `decodeWorkSecret()`
- `buildSdkUrl()`
- `sameSessionId()`
- `buildCCRv2SdkUrl()`
- `registerWorker()`

**Dependencies:** `axios`, `../utils/slowOperations`, `./types`

**Main flow:** Entry: `decodeWorkSecret()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `buddy/CompanionSprite.tsx` (371 lines)

**Exports:**
- `MIN_COLS_FOR_FULL_SPRITE`
- `companionReservedColumns()`
- `CompanionSprite()`
- `CompanionFloatingBubble()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `figures`, `react`, `../hooks/useTerminalSize`, `../ink/stringWidth`, `../ink`, `../state/AppState`, `../state/AppStateStore`, `../utils/config`

**Feature gates:** `BUDDY`

**Main flow:** Entry: `companionReservedColumns()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `buddy/companion.ts` (133 lines)

**Exports:**
- `Roll`
- `roll()`
- `rollWithSeed()`
- `companionUserId()`
- `getCompanion()`

**Dependencies:** `../utils/config`

**Main flow:** Entry: `roll()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `buddy/prompt.ts` (36 lines)

**Exports:**
- `companionIntroText()`
- `getCompanionIntroAttachment()`

**Dependencies:** `bun:bundle`, `../types/message`, `../utils/attachments`, `../utils/config`, `./companion`

**Feature gates:** `BUDDY`

**Main flow:** Entry: `companionIntroText()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `buddy/sprites.ts` (514 lines)

**Exports:**
- `renderSprite()`
- `spriteFrameCount()`
- `renderFace()`

**Dependencies:** `./types`

**Main flow:** Entry: `renderSprite()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `buddy/types.ts` (148 lines)

**Exports:**
- `RARITIES`
- `Rarity`
- `duck`
- `goose`
- `blob`
- `cat`
- `dragon`
- `octopus`
- `owl`
- `penguin`
- `turtle`
- `snail`
- `ghost`
- `axolotl`
- `capybara`
- `cactus`
- `robot`
- `rabbit`
- `mushroom`
- `chonk`
- `SPECIES`
- `Species`
- `EYES`
- `Eye`
- `HATS`
- ... +10 more

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `buddy/useBuddyNotification.tsx` (98 lines)

**Exports:**
- `isBuddyTeaserWindow()`
- `isBuddyLive()`
- `useBuddyNotification()`
- `findBuddyTriggerPositions()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `react`, `../context/notifications`, `../ink`, `../utils/config`, `../utils/thinking`

**Feature gates:** `BUDDY`

**Main flow:** Entry: `isBuddyTeaserWindow()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/add-dir/add-dir.tsx` (126 lines)

**Exports:**
- `call()`

**Dependencies:** `react/compiler-runtime`, `chalk`, `figures`, `react`, `../../bootstrap/state`, `../../commands`, `../../components/MessageResponse`, `../../components/permissions/rules/AddWorkspaceDirectory`, `../../ink`, `../../types/command`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/add-dir/index.ts` (11 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/add-dir/validation.ts` (110 lines)

**Exports:**
- `AddDirectoryResult`
- `validateDirectoryForWorkspace()`
- `addDirHelpMessage()`

**Dependencies:** `chalk`, `fs/promises`, `path`, `../../Tool`, `../../utils/errors`, `../../utils/path`

**Main flow:** Entry: `validateDirectoryForWorkspace()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/advisor.ts` (109 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../commands`, `../types/command`, `../utils/model/validateModel`, `../utils/settings/settings`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/agents/agents.tsx` (12 lines)

**Exports:**
- `call()`

**Dependencies:** `react`, `../../components/agents/AgentsMenu`, `../../Tool`, `../../tools`, `../../types/command`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/agents/index.ts` (10 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/branch/branch.ts` (296 lines)

**Exports:**
- `deriveFirstPrompt()`
- `call()`

**Dependencies:** `crypto`, `fs/promises`, `../../bootstrap/state`, `../../commands`, `../../services/analytics/index`, `../../types/command`, `../../utils/json`, `../../utils/slowOperations`, `../../utils/stringUtils`

**Main flow:** Entry: `deriveFirstPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/branch/index.ts` (14 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `bun:bundle`, `../../commands`

**Feature gates:** `FORK_SUBAGENT`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/bridge-kick.ts` (200 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../bridge/bridgeDebug`, `../commands`, `../types/command`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/bridge/bridge.tsx` (509 lines)

**Exports:**
- `call()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `qrcode`, `react`, `../../bridge/bridgeConfig`, `../../bridge/bridgeEnabled`, `../../bridge/envLessBridgeConfig`, `../../bridge/types`, `../../components/design-system/Dialog`

**Feature gates:** `KAIROS`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/bridge/index.ts` (26 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `bun:bundle`, `../../bridge/bridgeEnabled`, `../../commands`

**Feature gates:** `BRIDGE_MODE`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/brief.ts` (130 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `bun:bundle`, `zod/v4`, `../bootstrap/state`, `../services/analytics/growthbook`, `../Tool`, `../tools/BriefTool/BriefTool`, `../tools/BriefTool/prompt`, `../utils/lazySchema`

**Feature gates:** `KAIROS`, `KAIROS_BRIEF`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/btw/btw.tsx` (243 lines)

**Exports:**
- `call()`

**Dependencies:** `react/compiler-runtime`, `react`, `usehooks-ts`, `../../commands`, `../../components/Markdown`, `../../components/Spinner/SpinnerGlyph`, `../../constants/figures`, `../../constants/prompts`, `../../context/modalContext`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/btw/index.ts` (13 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/chrome/chrome.tsx` (285 lines)

**Exports:**
- `call`

**Dependencies:** `react/compiler-runtime`, `react`, `../../components/CustomSelect/select`, `../../components/design-system/Dialog`, `../../ink`, `../../state/AppState`, `../../utils/auth`, `../../utils/browser`, `../../utils/claudeInChrome/common`, `../../utils/claudeInChrome/setup`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/chrome/index.ts` (13 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../bootstrap/state`, `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/clear/caches.ts` (144 lines)

**Exports:**
- `clearSessionCaches()`

**Dependencies:** `bun:bundle`, `../../commands`, `../../constants/common`, `../../hooks/fileSuggestions`, `../../hooks/useSwarmPermissionPoller`, `../../services/api/dumpPrompts`, `../../services/api/promptCacheBreakDetection`, `../../services/api/sessionIngress`, `../../services/compact/postCompactCleanup`, `../../services/lsp/LSPDiagnosticRegistry`

**Feature gates:** `COMMIT_ATTRIBUTION`

**Main flow:** Entry: `clearSessionCaches()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/clear/clear.ts` (7 lines)

**Exports:**
- `call`

**Dependencies:** `../../types/command`, `./conversation`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/clear/conversation.ts` (251 lines)

**Exports:**
- `clearConversation()`

**Dependencies:** `bun:bundle`, `crypto`, `../../state/AppState`, `../../tasks/InProcessTeammateTask/types`, `../../tasks/LocalShellTask/guards`, `../../types/ids`, `../../types/message`, `../../utils/commitAttribution`, `../../utils/fileStateCache`, `../../utils/log`

**Feature gates:** `COORDINATOR_MODE`, `KAIROS`, `PROACTIVE`

**Main flow:** Entry: `clearConversation()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/clear/index.ts` (19 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/color/color.ts` (93 lines)

**Exports:**
- `call()`

**Dependencies:** `crypto`, `../../bootstrap/state`, `../../Tool`, `../../utils/teammate`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/color/index.ts` (16 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/commit-push-pr.ts` (158 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../commands`, `../utils/git`, `../utils/promptShellExecution`, `../utils/undercover`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/commit.ts` (92 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../commands`, `../utils/attribution`, `../utils/promptShellExecution`, `../utils/undercover`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/compact/compact.ts` (287 lines)

**Exports:**
- `call`

**Dependencies:** `bun:bundle`, `chalk`, `src/bootstrap/state`, `../../constants/prompts`, `../../context`, `../../keybindings/shortcutFormat`, `../../services/api/promptCacheBreakDetection`, `../../services/compact/compactWarningState`, `../../services/compact/microCompact`, `../../services/compact/postCompactCleanup`

**Feature gates:** `PROMPT_CACHE_BREAK_DETECTION`, `REACTIVE_COMPACT`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/compact/index.ts` (15 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../utils/envUtils`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/config/config.tsx` (7 lines)

**Exports:**
- `call`

**Dependencies:** `react`, `../../components/Settings/Settings`, `../../types/command`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/config/index.ts` (11 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/context/context-noninteractive.ts` (325 lines)

**Exports:**
- `collectContextData()`
- `call()`

**Dependencies:** `bun:bundle`, `../../services/compact/microCompact`, `../../state/AppStateStore`, `../../Tool`, `../../tools/AgentTool/loadAgentsDir`, `../../types/message`, `../../utils/format`, `../../utils/messages`, `../../utils/settings/constants`, `../../utils/stringUtils`

**Feature gates:** `CONTEXT_COLLAPSE`

**Main flow:** Entry: `collectContextData()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/context/context.tsx` (64 lines)

**Exports:**
- `call()`

**Dependencies:** `bun:bundle`, `react`, `../../commands`, `../../components/ContextVisualization`, `../../services/compact/microCompact`, `../../types/command`, `../../types/message`, `../../utils/analyzeContext`, `../../utils/messages`, `../../utils/staticRender`

**Feature gates:** `CONTEXT_COLLAPSE`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/context/index.ts` (24 lines)

**Exports:**
- `context`
- `contextNonInteractive`

**Dependencies:** `../../bootstrap/state`, `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/copy/copy.tsx` (371 lines)

**Exports:**
- `collectRecentAssistantTexts()`
- `fileExtension()`
- `call`

**Dependencies:** `react/compiler-runtime`, `fs/promises`, `marked`, `os`, `path`, `react`, `../../commands`, `../../components/CustomSelect/select`, `../../components/design-system/Byline`

**Main flow:** Entry: `collectRecentAssistantTexts()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/copy/index.ts` (15 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/cost/cost.ts` (24 lines)

**Exports:**
- `call`

**Dependencies:** `../../cost-tracker`, `../../services/claudeAiLimits`, `../../types/command`, `../../utils/auth`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/cost/index.ts` (23 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../utils/auth`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/createMovedToPluginCommand.ts` (65 lines)

**Exports:**
- `createMovedToPluginCommand()`

**Dependencies:** `@anthropic-ai/sdk/resources/messages`, `../commands`, `../Tool`

**Main flow:** Entry: `createMovedToPluginCommand()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/desktop/desktop.tsx` (9 lines)

**Exports:**
- `call()`

**Dependencies:** `react`, `../../commands`, `../../components/DesktopHandoff`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/desktop/index.ts` (26 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/diff/diff.tsx` (9 lines)

**Exports:**
- `call`

**Dependencies:** `react`, `../../types/command`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/diff/index.ts` (8 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/doctor/doctor.tsx` (7 lines)

**Exports:**
- `call`

**Dependencies:** `react`, `../../screens/Doctor`, `../../types/command`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/doctor/index.ts` (12 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../utils/envUtils`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/effort/effort.tsx` (183 lines)

**Exports:**
- `showCurrentEffort()`
- `executeEffort()`
- `call()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../hooks/useMainLoopModel`, `../../services/analytics/index`, `../../state/AppState`, `../../types/command`, `../../utils/effort`, `../../utils/settings/settings`

**Main flow:** Entry: `showCurrentEffort()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/effort/index.ts` (13 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../utils/immediateCommand`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/exit/exit.tsx` (33 lines)

**Exports:**
- `call()`

**Dependencies:** `bun:bundle`, `child_process`, `lodash-es/sample`, `react`, `../../components/ExitFlow`, `../../types/command`, `../../utils/concurrentSessions`, `../../utils/gracefulShutdown`, `../../utils/worktree`

**Feature gates:** `BG_SESSIONS`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/exit/index.ts` (12 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/export/export.tsx` (91 lines)

**Exports:**
- `extractFirstPrompt()`
- `sanitizeFilename()`
- `call()`

**Dependencies:** `path`, `react`, `../../components/ExportDialog`, `../../Tool`, `../../types/command`, `../../types/message`, `../../utils/cwd`, `../../utils/exportRenderer`, `../../utils/slowOperations`

**Main flow:** Entry: `extractFirstPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/export/index.ts` (11 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/extra-usage/extra-usage-core.ts` (118 lines)

**Exports:**
- `runExtraUsage()`

**Dependencies:** `../../services/api/overageCreditGrant`, `../../services/api/usage`, `../../utils/auth`, `../../utils/billing`, `../../utils/browser`, `../../utils/config`, `../../utils/log`

**Main flow:** Entry: `runExtraUsage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/extra-usage/extra-usage-noninteractive.ts` (16 lines)

**Exports:**
- `call()`

**Dependencies:** `./extra-usage-core`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/extra-usage/extra-usage.tsx` (17 lines)

**Exports:**
- `call()`

**Dependencies:** `react`, `../../commands`, `../../types/command`, `../login/login`, `./extra-usage-core`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/extra-usage/index.ts` (31 lines)

**Exports:**
- `extraUsage`
- `extraUsageNonInteractive`

**Dependencies:** `../../bootstrap/state`, `../../commands`, `../../utils/auth`, `../../utils/envUtils`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/fast/fast.tsx` (269 lines)

**Exports:**
- `FastModePicker()`
- `call()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../commands`, `../../components/design-system/Dialog`, `../../components/FastIcon`, `../../ink`, `../../keybindings/useKeybinding`, `../../services/analytics/index`, `../../state/AppState`

**Main flow:** Entry: `FastModePicker()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/fast/index.ts` (26 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../utils/immediateCommand`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/feedback/feedback.tsx` (25 lines)

**Exports:**
- `renderFeedbackComponent()`
- `call()`

**Dependencies:** `react`, `../../commands`, `../../components/Feedback`, `../../types/command`, `../../types/message`

**Main flow:** Entry: `renderFeedbackComponent()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/feedback/index.ts` (26 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../services/policyLimits/index`, `../../utils/envUtils`, `../../utils/privacyLevel`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/files/files.ts` (19 lines)

**Exports:**
- `call()`

**Dependencies:** `path`, `../../Tool`, `../../types/command`, `../../utils/cwd`, `../../utils/fileStateCache`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/files/index.ts` (12 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/heapdump/heapdump.ts` (17 lines)

**Exports:**
- `call()`

**Dependencies:** `../../utils/heapDumpService`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/heapdump/index.ts` (12 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/help/help.tsx` (11 lines)

**Exports:**
- `call`

**Dependencies:** `react`, `../../components/HelpV2/HelpV2`, `../../types/command`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/help/index.ts` (10 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/hooks/hooks.tsx` (13 lines)

**Exports:**
- `call`

**Dependencies:** `react`, `../../components/hooks/HooksConfigMenu`, `../../services/analytics/index`, `../../tools`, `../../types/command`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/hooks/index.ts` (11 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/ide/ide.tsx` (646 lines)

**Exports:**
- `call()`
- `formatWorkspaceFolders()`

**Dependencies:** `react/compiler-runtime`, `chalk`, `path`, `react`, `src/services/analytics/index`, `../../commands`, `../../components/CustomSelect/index`, `../../components/design-system/Dialog`, `../../components/IdeAutoConnectDialog`, `../../ink`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/ide/index.ts` (11 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/init-verifiers.ts` (262 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/init.ts` (256 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `bun:bundle`, `../commands`, `../projectOnboardingState`, `../utils/envUtils`

**Feature gates:** `NEW_INIT`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/insights.ts` (3200 lines)

**Exports:**
- `deduplicateSessionBranches()`
- `detectMultiClauding()`
- `InsightsExport`
- `buildExportData()`
- `generateUsageReport()`

**Dependencies:** `child_process`, `diff`, `fs`, `os`, `path`, `../commands`, `../services/api/claude`, `../types/logs`, `../utils/envUtils`, `../utils/errors`

**Main flow:** Entry: `deduplicateSessionBranches()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/install-github-app/ApiKeyStep.tsx` (231 lines)

**Exports:**
- `ApiKeyStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../components/TextInput`, `../../hooks/useTerminalSize`, `../../ink`, `../../keybindings/useKeybinding`

**Main flow:** Entry: `ApiKeyStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/install-github-app/CheckExistingSecretStep.tsx` (190 lines)

**Exports:**
- `CheckExistingSecretStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../components/TextInput`, `../../hooks/useTerminalSize`, `../../ink`, `../../keybindings/useKeybinding`

**Main flow:** Entry: `CheckExistingSecretStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/install-github-app/CheckGitHubStep.tsx` (15 lines)

**Exports:**
- `CheckGitHubStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`

**Main flow:** Entry: `CheckGitHubStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/install-github-app/ChooseRepoStep.tsx` (211 lines)

**Exports:**
- `ChooseRepoStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../components/TextInput`, `../../hooks/useTerminalSize`, `../../ink`, `../../keybindings/useKeybinding`

**Main flow:** Entry: `ChooseRepoStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/install-github-app/CreatingStep.tsx` (65 lines)

**Exports:**
- `CreatingStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `./types`

**Main flow:** Entry: `CreatingStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/install-github-app/ErrorStep.tsx` (85 lines)

**Exports:**
- `ErrorStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../constants/github-app`, `../../ink`

**Main flow:** Entry: `ErrorStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/install-github-app/ExistingWorkflowStep.tsx` (103 lines)

**Exports:**
- `ExistingWorkflowStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/components/CustomSelect/index`, `../../ink`

**Main flow:** Entry: `ExistingWorkflowStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/install-github-app/InstallAppStep.tsx` (94 lines)

**Exports:**
- `InstallAppStep()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../constants/github-app`, `../../ink`, `../../keybindings/useKeybinding`

**Main flow:** Entry: `InstallAppStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/install-github-app/OAuthFlowStep.tsx` (276 lines)

**Exports:**
- `OAuthFlowStep()`

**Dependencies:** `react`, `src/services/analytics/index`, `../../components/design-system/KeyboardShortcutHint`, `../../components/Spinner`, `../../components/TextInput`, `../../hooks/useTerminalSize`, `../../ink/events/keyboard-event`, `../../ink/termio/osc`, `../../ink`, `../../services/oauth/index`

**Main flow:** Entry: `OAuthFlowStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/install-github-app/SuccessStep.tsx` (96 lines)

**Exports:**
- `SuccessStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`

**Main flow:** Entry: `SuccessStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/install-github-app/WarningsStep.tsx` (73 lines)

**Exports:**
- `WarningsStep()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../constants/github-app`, `../../ink`, `../../keybindings/useKeybinding`, `./types`

**Main flow:** Entry: `WarningsStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/install-github-app/index.ts` (13 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../utils/envUtils`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/install-github-app/install-github-app.tsx` (587 lines)

**Exports:**
- `call()`

**Dependencies:** `execa`, `react`, `src/services/analytics/index`, `../../components/WorkflowMultiselectDialog`, `../../constants/github-app`, `../../hooks/useExitOnCtrlCDWithKeybindings`, `../../ink/events/keyboard-event`, `../../ink`, `../../types/command`, `../../utils/auth`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/install-github-app/setupGitHubActions.ts` (325 lines)

**Exports:**
- `setupGitHubActions()`

**Dependencies:** `src/utils/config`, `../../utils/browser`, `../../utils/execFileNoThrow`, `../../utils/log`, `./types`

**Main flow:** Entry: `setupGitHubActions()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/install-slack-app/index.ts` (12 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/install-slack-app/install-slack-app.ts` (30 lines)

**Exports:**
- `call()`

**Dependencies:** `../../commands`, `../../services/analytics/index`, `../../utils/browser`, `../../utils/config`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/install.tsx` (300 lines)

**Exports:**
- `install`

**Dependencies:** `react/compiler-runtime`, `node:os`, `node:path`, `react`, `src/commands`, `src/services/analytics/index`, `../components/design-system/StatusIcon`, `../ink`, `../utils/debug`, `../utils/env`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/keybindings/index.ts` (13 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../keybindings/loadUserBindings`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/keybindings/keybindings.ts` (53 lines)

**Exports:**
- `call()`

**Dependencies:** `fs/promises`, `path`, `../../keybindings/template`, `../../utils/errors`, `../../utils/promptEditor`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/login/index.ts` (14 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../utils/auth`, `../../utils/envUtils`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/login/login.tsx` (104 lines)

**Exports:**
- `call()`
- `Login()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `react`, `../../bootstrap/state`, `../../bridge/trustedDevice`, `../../commands`, `../../components/ConfigurableShortcutHint`, `../../components/ConsoleOAuthFlow`, `../../components/design-system/Dialog`, `../../hooks/useMainLoopModel`

**Feature gates:** `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/logout/index.ts` (10 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../utils/envUtils`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/logout/logout.tsx` (82 lines)

**Exports:**
- `performLogout()`
- `clearAuthRelatedCaches()`
- `call()`

**Dependencies:** `react`, `../../bridge/trustedDevice`, `../../ink`, `../../services/analytics/growthbook`, `../../services/api/grove`, `../../services/policyLimits/index`, `../../services/remoteManagedSettings/index`, `../../utils/auth`, `../../utils/betas`, `../../utils/config`

**Main flow:** Entry: `performLogout()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/mcp/addCommand.ts` (280 lines)

**Exports:**
- `registerMcpAddCommand()`

**Dependencies:** `@commander-js/extra-typings`, `../../cli/exit`, `../../services/mcp/config`, `../../utils/envUtils`, `../../utils/slowOperations`

**Main flow:** Entry: `registerMcpAddCommand()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/mcp/index.ts` (12 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/mcp/mcp.tsx` (85 lines)

**Exports:**
- `call()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../components/mcp/index`, `../../components/mcp/MCPReconnect`, `../../services/mcp/MCPConnectionManager`, `../../state/AppState`, `../../types/command`, `../plugin/PluginSettings`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/mcp/xaaIdpCommand.ts` (266 lines)

**Exports:**
- `registerMcpXaaIdpCommand()`

**Dependencies:** `@commander-js/extra-typings`, `../../cli/exit`, `../../utils/errors`, `../../utils/settings/settings`

**Main flow:** Entry: `registerMcpXaaIdpCommand()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/memory/index.ts` (10 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/memory/memory.tsx` (90 lines)

**Exports:**
- `call`

**Dependencies:** `fs/promises`, `react`, `../../commands`, `../../components/design-system/Dialog`, `../../components/memory/MemoryFileSelector`, `../../components/memory/MemoryUpdateNotification`, `../../ink`, `../../types/command`, `../../utils/claudemd`, `../../utils/envUtils`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/mobile/index.ts` (11 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/mobile/mobile.tsx` (274 lines)

**Exports:**
- `call()`

**Dependencies:** `react/compiler-runtime`, `qrcode`, `react`, `../../components/design-system/Pane`, `../../ink/events/keyboard-event`, `../../ink`, `../../keybindings/useKeybinding`, `../../types/command`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/model/index.ts` (16 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../utils/immediateCommand`, `../../utils/model/model`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/model/model.tsx` (297 lines)

**Exports:**
- `call`

**Dependencies:** `react/compiler-runtime`, `chalk`, `react`, `../../commands`, `../../components/ModelPicker`, `../../constants/xml`, `../../services/analytics/index`, `../../state/AppState`, `../../types/command`, `../../utils/effort`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/output-style/index.ts` (11 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/output-style/output-style.tsx` (7 lines)

**Exports:**
- `call()`

**Dependencies:** `../../types/command`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/passes/index.ts` (22 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/passes/passes.tsx` (24 lines)

**Exports:**
- `call()`

**Dependencies:** `react`, `../../components/Passes/Passes`, `../../services/analytics/index`, `../../services/api/referral`, `../../types/command`, `../../utils/config`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/permissions/index.ts` (11 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/permissions/permissions.tsx` (10 lines)

**Exports:**
- `call`

**Dependencies:** `react`, `../../components/permissions/rules/PermissionRuleList`, `../../types/command`, `../../utils/messages`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plan/index.ts` (11 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plan/plan.tsx` (122 lines)

**Exports:**
- `call()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../bootstrap/state`, `../../commands`, `../../ink`, `../../types/command`, `../../utils/editor`, `../../utils/ide`, `../../utils/permissions/PermissionUpdate`, `../../utils/permissions/permissionSetup`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plugin/AddMarketplace.tsx` (162 lines)

**Exports:**
- `AddMarketplace()`

**Dependencies:** `react`, `src/services/analytics/index`, `../../components/ConfigurableShortcutHint`, `../../components/design-system/Byline`, `../../components/design-system/KeyboardShortcutHint`, `../../components/Spinner`, `../../components/TextInput`, `../../ink`, `../../utils/errors`

**Main flow:** Entry: `AddMarketplace()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plugin/BrowseMarketplace.tsx` (802 lines)

**Exports:**
- `BrowseMarketplace()`

**Dependencies:** `figures`, `react`, `../../components/ConfigurableShortcutHint`, `../../components/design-system/Byline`, `../../ink`, `../../keybindings/useKeybinding`, `../../types/plugin`, `../../utils/array`, `../../utils/browser`

**Main flow:** Entry: `BrowseMarketplace()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plugin/DiscoverPlugins.tsx` (781 lines)

**Exports:**
- `DiscoverPlugins()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../components/ConfigurableShortcutHint`, `../../components/design-system/Byline`, `../../components/SearchBox`, `../../hooks/useSearchInput`, `../../hooks/useTerminalSize`, `../../ink`

**Main flow:** Entry: `DiscoverPlugins()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plugin/ManageMarketplaces.tsx` (838 lines)

**Exports:**
- `ManageMarketplaces()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `src/services/analytics/index`, `../../components/ConfigurableShortcutHint`, `../../components/design-system/Byline`, `../../components/design-system/KeyboardShortcutHint`, `../../ink`, `../../keybindings/useKeybinding`

**Main flow:** Entry: `ManageMarketplaces()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plugin/ManagePlugins.tsx` (2215 lines)

**Exports:**
- `filterManagedDisabledPlugins()`
- `ManagePlugins()`

**Dependencies:** `figures`, `fs`, `fs/promises`, `path`, `react`, `../../components/ConfigurableShortcutHint`, `../../components/design-system/Byline`, `../../components/mcp/MCPRemoteServerMenu`, `../../components/mcp/MCPStdioServerMenu`

**Main flow:** Entry: `filterManagedDisabledPlugins()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plugin/PluginErrors.tsx` (124 lines)

**Exports:**
- `formatErrorMessage()`
- `getErrorGuidance()`

**Dependencies:** `../../types/plugin`

**Main flow:** Entry: `formatErrorMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plugin/PluginOptionsDialog.tsx` (357 lines)

**Exports:**
- `buildFinalValues()`
- `PluginOptionsDialog()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../components/design-system/Dialog`, `../../ink/stringWidth`, `../../ink`, `../../keybindings/useKeybinding`, `../../utils/envUtils`, `../../utils/plugins/pluginOptionsStorage`

**Main flow:** Entry: `buildFinalValues()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plugin/PluginOptionsFlow.tsx` (135 lines)

**Exports:**
- `findPluginOptionsTarget()`
- `PluginOptionsFlow()`

**Dependencies:** `react`, `../../types/plugin`, `../../utils/errors`, `../../utils/plugins/mcpbHandler`, `../../utils/plugins/mcpPluginIntegration`, `../../utils/plugins/pluginLoader`, `../../utils/plugins/pluginOptionsStorage`, `./PluginOptionsDialog`

**Main flow:** Entry: `findPluginOptionsTarget()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plugin/PluginSettings.tsx` (1072 lines)

**Exports:**
- `PluginSettings()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../components/ConfigurableShortcutHint`, `../../components/design-system/Byline`, `../../components/design-system/Pane`, `../../components/design-system/Tabs`, `../../hooks/useExitOnCtrlCDWithKeybindings`, `../../ink`

**Main flow:** Entry: `PluginSettings()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plugin/PluginTrustWarning.tsx` (32 lines)

**Exports:**
- `PluginTrustWarning()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../ink`, `../../utils/plugins/marketplaceHelpers`

**Main flow:** Entry: `PluginTrustWarning()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plugin/UnifiedInstalledCell.tsx` (565 lines)

**Exports:**
- `UnifiedInstalledCell()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../ink`, `../../utils/stringUtils`, `./unifiedTypes`

**Main flow:** Entry: `UnifiedInstalledCell()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plugin/ValidatePlugin.tsx` (98 lines)

**Exports:**
- `ValidatePlugin()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../ink`, `../../utils/errors`, `../../utils/log`, `../../utils/plugins/validatePlugin`, `../../utils/stringUtils`

**Main flow:** Entry: `ValidatePlugin()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plugin/index.tsx` (11 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plugin/parseArgs.ts` (103 lines)

**Exports:**
- `ParsedCommand`
- `parsePluginArgs()`

**Dependencies:** local only

**Main flow:** Entry: `parsePluginArgs()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plugin/plugin.tsx` (7 lines)

**Exports:**
- `call()`

**Dependencies:** `react`, `../../types/command`, `./PluginSettings`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plugin/pluginDetailsHelpers.tsx` (117 lines)

**Exports:**
- `InstallablePlugin`
- `PluginDetailsMenuOption`
- `extractGitHubRepo()`
- `buildPluginDetailsMenuOptions()`
- `PluginSelectionKeyHint()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../components/ConfigurableShortcutHint`, `../../components/design-system/Byline`, `../../ink`, `../../utils/plugins/schemas`

**Main flow:** Entry: `extractGitHubRepo()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/plugin/usePagination.ts` (171 lines)

**Exports:**
- `usePagination()`

**Dependencies:** `react`

**Main flow:** Entry: `usePagination()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/pr_comments/index.ts` (50 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../createMovedToPluginCommand`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/privacy-settings/index.ts` (14 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../utils/auth`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/privacy-settings/privacy-settings.tsx` (58 lines)

**Exports:**
- `call()`

**Dependencies:** `react`, `../../components/grove/Grove`, `../../services/analytics/index`, `../../services/api/grove`, `../../types/command`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/rate-limit-options/index.ts` (19 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../utils/auth`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/rate-limit-options/rate-limit-options.tsx` (210 lines)

**Exports:**
- `call()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../commands`, `../../components/CustomSelect/select`, `../../components/design-system/Dialog`, `../../services/analytics/growthbook`, `../../services/analytics/index`, `../../services/claudeAiLimitsHook`, `../../Tool`, `../../types/command`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/release-notes/index.ts` (11 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/release-notes/release-notes.ts` (50 lines)

**Exports:**
- `call()`

**Dependencies:** `../../types/command`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/reload-plugins/index.ts` (18 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/reload-plugins/reload-plugins.ts` (61 lines)

**Exports:**
- `call`

**Dependencies:** `bun:bundle`, `../../bootstrap/state`, `../../services/settingsSync/index`, `../../types/command`, `../../utils/envUtils`, `../../utils/plugins/refresh`, `../../utils/settings/changeDetector`, `../../utils/stringUtils`

**Feature gates:** `DOWNLOAD_USER_SETTINGS`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/remote-env/index.ts` (15 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../services/policyLimits/index`, `../../utils/auth`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/remote-env/remote-env.tsx` (7 lines)

**Exports:**
- `call()`

**Dependencies:** `react`, `../../components/RemoteEnvironmentDialog`, `../../types/command`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/remote-setup/api.ts` (182 lines)

**Exports:**
- `RedactedGithubToken`
- `ImportTokenResult`
- `ImportTokenError`
- `importGithubToken()`
- `createDefaultEnvironment()`
- `isSignedIn()`
- `getCodeWebUrl()`

**Dependencies:** `axios`, `../../constants/oauth`, `../../utils/debug`, `../../utils/teleport/api`, `../../utils/teleport/environments`

**Main flow:** Entry: `importGithubToken()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/remote-setup/index.ts` (20 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../services/analytics/growthbook`, `../../services/policyLimits/index`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/remote-setup/remote-setup.tsx` (187 lines)

**Exports:**
- `call()`

**Dependencies:** `execa`, `react`, `../../components/CustomSelect/index`, `../../components/design-system/Dialog`, `../../components/design-system/LoadingState`, `../../ink`, `../../services/analytics/index`, `../../types/command`, `../../utils/browser`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/rename/generateSessionName.ts` (67 lines)

**Exports:**
- `generateSessionName()`

**Dependencies:** `../../services/api/claude`, `../../types/message`, `../../utils/debug`, `../../utils/errors`, `../../utils/json`, `../../utils/messages`, `../../utils/sessionTitle`, `../../utils/systemPromptType`

**Main flow:** Entry: `generateSessionName()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/rename/index.ts` (12 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/rename/rename.ts` (87 lines)

**Exports:**
- `call()`

**Dependencies:** `crypto`, `../../bootstrap/state`, `../../Tool`, `../../utils/messages`, `../../utils/teammate`, `./generateSessionName`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/resume/index.ts` (12 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/resume/resume.tsx` (275 lines)

**Exports:**
- `filterResumableSessions()`
- `call`

**Dependencies:** `react/compiler-runtime`, `chalk`, `crypto`, `figures`, `react`, `../../bootstrap/state`, `../../commands`, `../../components/LogSelector`, `../../components/MessageResponse`, `../../components/Spinner`

**Main flow:** Entry: `filterResumableSessions()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/review.ts` (57 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `@anthropic-ai/sdk/resources/messages`, `../commands`, `./review/ultrareviewEnabled`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/review/UltrareviewOverageDialog.tsx` (96 lines)

**Exports:**
- `UltrareviewOverageDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../components/CustomSelect/select`, `../../components/design-system/Dialog`, `../../ink`

**Main flow:** Entry: `UltrareviewOverageDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/review/reviewRemote.ts` (316 lines)

**Exports:**
- `confirmOverage()`
- `OverageGate`
- `checkOverageGate()`
- `launchRemoteReview()`

**Dependencies:** `@anthropic-ai/sdk/resources/messages`, `../../services/analytics/growthbook`, `../../services/api/ultrareviewQuota`, `../../services/api/usage`, `../../Tool`, `../../utils/auth`, `../../utils/detectRepository`, `../../utils/execFileNoThrow`, `../../utils/git`, `../../utils/teleport`

**Main flow:** Entry: `confirmOverage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/review/ultrareviewCommand.tsx` (58 lines)

**Exports:**
- `call`

**Dependencies:** `@anthropic-ai/sdk/resources/messages`, `react`, `../../types/command`, `./reviewRemote`, `./UltrareviewOverageDialog`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/review/ultrareviewEnabled.ts` (14 lines)

**Exports:**
- `isUltrareviewEnabled()`

**Dependencies:** `../../services/analytics/growthbook`

**Main flow:** Entry: `isUltrareviewEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/rewind/index.ts` (13 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/rewind/rewind.ts` (13 lines)

**Exports:**
- `call()`

**Dependencies:** `../../commands`, `../../Tool`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/sandbox-toggle/index.ts` (50 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `figures`, `../../commands`, `../../utils/sandbox/sandbox-adapter`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/sandbox-toggle/sandbox-toggle.tsx` (83 lines)

**Exports:**
- `call()`

**Dependencies:** `path`, `react`, `../../bootstrap/state`, `../../components/sandbox/SandboxSettings`, `../../ink`, `../../utils/platform`, `../../utils/sandbox/sandbox-adapter`, `../../utils/settings/settings`, `../../utils/theme`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/security-review.ts` (243 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../utils/frontmatterParser`, `../utils/markdownConfigLoader`, `../utils/promptShellExecution`, `./createMovedToPluginCommand`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/session/index.ts` (16 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../bootstrap/state`, `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/session/session.tsx` (140 lines)

**Exports:**
- `call`

**Dependencies:** `react/compiler-runtime`, `qrcode`, `react`, `../../components/design-system/Pane`, `../../ink`, `../../keybindings/useKeybinding`, `../../state/AppState`, `../../types/command`, `../../utils/debug`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/skills/index.ts` (10 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/skills/skills.tsx` (8 lines)

**Exports:**
- `call()`

**Dependencies:** `react`, `../../commands`, `../../components/skills/SkillsMenu`, `../../types/command`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/stats/index.ts` (10 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/stats/stats.tsx` (7 lines)

**Exports:**
- `call`

**Dependencies:** `react`, `../../components/Stats`, `../../types/command`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/status/index.ts` (12 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/status/status.tsx` (8 lines)

**Exports:**
- `call()`

**Dependencies:** `react`, `../../commands`, `../../components/Settings/Settings`, `../../types/command`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/statusline.tsx` (24 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `@anthropic-ai/sdk/resources/index.mjs`, `../commands`, `../tools/AgentTool/constants`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/stickers/index.ts` (11 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/stickers/stickers.ts` (16 lines)

**Exports:**
- `call()`

**Dependencies:** `../../types/command`, `../../utils/browser`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/tag/index.ts` (12 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/tag/tag.tsx` (215 lines)

**Exports:**
- `call()`

**Dependencies:** `react/compiler-runtime`, `chalk`, `crypto`, `react`, `../../bootstrap/state`, `../../commands`, `../../components/CustomSelect/select`, `../../components/design-system/Dialog`, `../../constants/xml`, `../../ink`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/tasks/index.ts` (11 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/tasks/tasks.tsx` (8 lines)

**Exports:**
- `call()`

**Dependencies:** `react`, `../../commands`, `../../components/tasks/BackgroundTasksDialog`, `../../types/command`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/terminalSetup/index.ts` (23 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../utils/env`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/terminalSetup/terminalSetup.tsx` (531 lines)

**Exports:**
- `getNativeCSIuTerminalDisplayName()`
- `shouldOfferTerminalSetup()`
- `setupTerminal()`
- `isShiftEnterKeyBindingInstalled()`
- `hasUsedBackslashReturn()`
- `markBackslashReturnUsed()`
- `call()`

**Dependencies:** `chalk`, `crypto`, `fs/promises`, `os`, `path`, `src/utils/theme`, `url`, `../../ink/supports-hyperlinks`, `../../ink`, `../../projectOnboardingState`

**Main flow:** Entry: `getNativeCSIuTerminalDisplayName()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/theme/index.ts` (10 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/theme/theme.tsx` (57 lines)

**Exports:**
- `call`

**Dependencies:** `react/compiler-runtime`, `react`, `../../commands`, `../../components/design-system/Pane`, `../../components/ThemePicker`, `../../ink`, `../../types/command`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/thinkback-play/index.ts` (17 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../services/analytics/growthbook`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/thinkback-play/thinkback-play.ts` (43 lines)

**Exports:**
- `call()`

**Dependencies:** `path`, `../../commands`, `../../utils/plugins/installedPluginsManager`, `../../utils/plugins/officialMarketplace`, `../thinkback/thinkback`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/thinkback/index.ts` (13 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../services/analytics/growthbook`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/thinkback/thinkback.tsx` (554 lines)

**Exports:**
- `playAnimation()`
- `call()`

**Dependencies:** `react/compiler-runtime`, `execa`, `fs/promises`, `path`, `react`, `../../commands`, `../../components/CustomSelect/select`, `../../components/design-system/Dialog`, `../../components/Spinner`

**Main flow:** Entry: `playAnimation()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/ultraplan.tsx` (471 lines)

**Exports:**
- `CCR_TERMS_URL`
- `buildUltraplanPrompt()`
- `stopUltraplan()`
- `launchUltraplan()`

**Dependencies:** `fs`, `../bridge/types`, `../commands`, `../constants/figures`, `../constants/product`, `../services/analytics/growthbook`, `../services/analytics/index`, `../state/AppStateStore`, `../tasks/RemoteAgentTask/RemoteAgentTask`, `../types/command`

**Main flow:** Entry: `buildUltraplanPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/upgrade/index.ts` (16 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`, `../../utils/auth`, `../../utils/envUtils`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/upgrade/upgrade.tsx` (38 lines)

**Exports:**
- `call()`

**Dependencies:** `react`, `../../commands`, `../../services/oauth/getOauthProfile`, `../../types/command`, `../../utils/auth`, `../../utils/browser`, `../../utils/log`, `../login/login`

**Main flow:** Entry: `call()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/usage/index.ts` (9 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/usage/usage.tsx` (7 lines)

**Exports:**
- `call`

**Dependencies:** `react`, `../../components/Settings/Settings`, `../../types/command`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/version.ts` (22 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../types/command`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/vim/index.ts` (11 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/vim/vim.ts` (38 lines)

**Exports:**
- `call`

**Dependencies:** `../../types/command`, `../../utils/config`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/voice/index.ts` (20 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../../commands`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `commands/voice/voice.ts` (150 lines)

**Exports:**
- `call`

**Dependencies:** `../../hooks/useVoice`, `../../keybindings/shortcutFormat`, `../../services/analytics/index`, `../../types/command`, `../../utils/auth`, `../../utils/config`, `../../utils/settings/changeDetector`, `../../voice/voiceModeEnabled`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/AgentProgressLine.tsx` (136 lines)

**Exports:**
- `AgentProgressLine()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `../utils/format`, `../utils/theme`

**Main flow:** Entry: `AgentProgressLine()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/App.tsx` (56 lines)

**Exports:**
- `App()`

**Dependencies:** `react/compiler-runtime`, `react`, `../context/fpsMetrics`, `../context/stats`, `../state/AppState`, `../state/onChangeAppState`, `../utils/fpsTracker`

**Main flow:** Entry: `App()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ApproveApiKey.tsx` (123 lines)

**Exports:**
- `ApproveApiKey()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `../utils/config`, `./CustomSelect/index`, `./design-system/Dialog`

**Main flow:** Entry: `ApproveApiKey()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/AutoModeOptInDialog.tsx` (142 lines)

**Exports:**
- `AUTO_MODE_DESCRIPTION`
- `AutoModeOptInDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/services/analytics/index`, `../ink`, `../utils/settings/settings`, `./CustomSelect/index`, `./design-system/Dialog`

**Main flow:** Entry: `AutoModeOptInDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/AutoUpdater.tsx` (198 lines)

**Exports:**
- `AutoUpdater()`

**Dependencies:** `react`, `src/services/analytics/index`, `usehooks-ts`, `../hooks/useUpdateNotification`, `../ink`, `../utils/autoUpdater`, `../utils/config`, `../utils/debug`, `../utils/doctorDiagnostic`

**Main flow:** Entry: `AutoUpdater()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/AutoUpdaterWrapper.tsx` (91 lines)

**Exports:**
- `AutoUpdaterWrapper()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `react`, `../utils/autoUpdater`, `../utils/config`, `../utils/debug`, `../utils/doctorDiagnostic`, `./AutoUpdater`, `./NativeAutoUpdater`, `./PackageManagerAutoUpdater`

**Feature gates:** `SKIP_DETECTION_WHEN_AUTOUPDATES_DISABLED`

**Main flow:** Entry: `AutoUpdaterWrapper()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/AwsAuthStatusBox.tsx` (82 lines)

**Exports:**
- `AwsAuthStatusBox()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `../utils/awsAuthStatusManager`

**Main flow:** Entry: `AwsAuthStatusBox()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/BaseTextInput.tsx` (136 lines)

**Exports:**
- `BaseTextInput()`

**Dependencies:** `react/compiler-runtime`, `react`, `../hooks/renderPlaceholder`, `../hooks/usePasteHandler`, `../ink/hooks/use-declared-cursor`, `../ink`, `../types/textInputTypes`, `../utils/textHighlighting`, `./PromptInput/ShimmeredInput`

**Main flow:** Entry: `BaseTextInput()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/BashModeProgress.tsx` (56 lines)

**Exports:**
- `BashModeProgress()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `../tools/BashTool/BashTool`, `../types/tools`, `./messages/UserBashInputMessage`, `./shell/ShellProgressMessage`

**Main flow:** Entry: `BashModeProgress()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/BridgeDialog.tsx` (401 lines)

**Exports:**
- `BridgeDialog()`

**Dependencies:** `react/compiler-runtime`, `path`, `qrcode`, `react`, `../bootstrap/state`, `../bridge/bridgeStatusUtil`, `../constants/figures`, `../context/overlayContext`, `../ink`

**Main flow:** Entry: `BridgeDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/BypassPermissionsModeDialog.tsx` (87 lines)

**Exports:**
- `BypassPermissionsModeDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/services/analytics/index`, `../ink`, `../utils/gracefulShutdown`, `../utils/settings/settings`, `./CustomSelect/index`, `./design-system/Dialog`

**Main flow:** Entry: `BypassPermissionsModeDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ChannelDowngradeDialog.tsx` (102 lines)

**Exports:**
- `ChannelDowngradeChoice`
- `ChannelDowngradeDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `./CustomSelect/index`, `./design-system/Dialog`

**Main flow:** Entry: `ChannelDowngradeDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ClaudeCodeHint/PluginHintMenu.tsx` (78 lines)

**Exports:**
- `PluginHintMenu()`

**Dependencies:** `react`, `../../ink`, `../CustomSelect/select`, `../permissions/PermissionDialog`

**Main flow:** Entry: `PluginHintMenu()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ClaudeInChromeOnboarding.tsx` (121 lines)

**Exports:**
- `ClaudeInChromeOnboarding()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/services/analytics/index`, `../ink`, `../utils/claudeInChrome/setup`, `../utils/config`, `./design-system/Dialog`

**Main flow:** Entry: `ClaudeInChromeOnboarding()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ClaudeMdExternalIncludesDialog.tsx` (137 lines)

**Exports:**
- `ClaudeMdExternalIncludesDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/services/analytics/index`, `../ink`, `../utils/claudemd`, `../utils/config`, `./CustomSelect/index`, `./design-system/Dialog`

**Main flow:** Entry: `ClaudeMdExternalIncludesDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ClickableImageRef.tsx` (73 lines)

**Exports:**
- `ClickableImageRef()`

**Dependencies:** `react/compiler-runtime`, `react`, `url`, `../ink/components/Link`, `../ink/supports-hyperlinks`, `../ink`, `../utils/imageStore`, `../utils/theme`

**Main flow:** Entry: `ClickableImageRef()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/CompactSummary.tsx` (118 lines)

**Exports:**
- `CompactSummary()`

**Dependencies:** `react/compiler-runtime`, `react`, `../constants/figures`, `../ink`, `../screens/REPL`, `../types/message`, `../utils/messages`, `./ConfigurableShortcutHint`, `./MessageResponse`

**Main flow:** Entry: `CompactSummary()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ConfigurableShortcutHint.tsx` (57 lines)

**Exports:**
- `ConfigurableShortcutHint()`

**Dependencies:** `react/compiler-runtime`, `react`, `../keybindings/types`, `../keybindings/useShortcutDisplay`, `./design-system/KeyboardShortcutHint`

**Main flow:** Entry: `ConfigurableShortcutHint()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ConsoleOAuthFlow.tsx` (631 lines)

**Exports:**
- `ConsoleOAuthFlow()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/services/analytics/index`, `../cli/handlers/auth`, `../hooks/useTerminalSize`, `../ink/termio/osc`, `../ink/useTerminalNotification`, `../ink`, `../keybindings/useKeybinding`, `../services/api/errorUtils`

**Main flow:** Entry: `ConsoleOAuthFlow()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ContextSuggestions.tsx` (47 lines)

**Exports:**
- `ContextSuggestions()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../ink`, `../utils/contextSuggestions`, `../utils/format`, `./design-system/StatusIcon`

**Main flow:** Entry: `ContextSuggestions()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ContextVisualization.tsx` (489 lines)

**Exports:**
- `ContextVisualization()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `react`, `../ink`, `../utils/analyzeContext`, `../utils/contextSuggestions`, `../utils/file`, `../utils/format`, `../utils/settings/constants`, `../utils/stringUtils`

**Feature gates:** `CONTEXT_COLLAPSE`

**Main flow:** Entry: `ContextVisualization()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/CoordinatorAgentStatus.tsx` (273 lines)

**Exports:**
- `getVisibleAgentTasks()`
- `CoordinatorTaskPanel()`
- `useCoordinatorTaskCount()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../constants/figures`, `../hooks/useTerminalSize`, `../ink/stringWidth`, `../ink`, `../state/AppState`, `../state/teammateViewHelpers`, `../tasks/LocalAgentTask/LocalAgentTask`

**Main flow:** Entry: `getVisibleAgentTasks()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/CostThresholdDialog.tsx` (50 lines)

**Exports:**
- `CostThresholdDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `./CustomSelect/index`, `./design-system/Dialog`

**Main flow:** Entry: `CostThresholdDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/CtrlOToExpand.tsx` (51 lines)

**Exports:**
- `SubAgentProvider()`
- `CtrlOToExpand()`
- `ctrlOToExpand()`

**Dependencies:** `react/compiler-runtime`, `chalk`, `react`, `../ink`, `../keybindings/shortcutFormat`, `../keybindings/useShortcutDisplay`, `./design-system/KeyboardShortcutHint`, `./messageActions`

**Main flow:** Entry: `SubAgentProvider()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/CustomSelect/SelectMulti.tsx` (213 lines)

**Exports:**
- `SelectMultiProps`
- `SelectMulti()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../ink`, `../../utils/config`, `../../utils/imageResizer`, `./select`, `./select-input-option`, `./select-option`, `./use-multi-select-state`

**Main flow:** Entry: `SelectMulti()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/CustomSelect/index.ts` (3 lines)

**Exports:**
- (none — internal module)

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/CustomSelect/option-map.ts` (50 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `react`, `./select`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/CustomSelect/select-input-option.tsx` (488 lines)

**Exports:**
- `SelectInputOption()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../keybindings/useKeybinding`, `../../utils/config`, `../../utils/imagePaste`, `../../utils/imageResizer`, `../ClickableImageRef`, `../ConfigurableShortcutHint`, `../design-system/Byline`

**Main flow:** Entry: `SelectInputOption()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/CustomSelect/select-option.tsx` (68 lines)

**Exports:**
- `SelectOptionProps`
- `SelectOption()`

**Dependencies:** `react/compiler-runtime`, `react`, `../design-system/ListItem`

**Main flow:** Entry: `SelectOption()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/CustomSelect/select.tsx` (690 lines)

**Exports:**
- `OptionWithDescription`
- `SelectProps`
- `Select()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../ink/hooks/use-declared-cursor`, `../../ink/stringWidth`, `../../ink`, `../../utils/array`, `../../utils/config`, `../../utils/imageResizer`, `./select-input-option`

**Main flow:** Entry: `Select()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/CustomSelect/use-multi-select-state.ts` (414 lines)

**Exports:**
- `UseMultiSelectStateProps`
- `MultiSelectState`
- `useMultiSelectState()`

**Dependencies:** `react`, `util`, `../../context/overlayContext`, `../../ink/events/input-event`, `../../ink`, `./select`, `./use-select-navigation`

**Main flow:** Entry: `useMultiSelectState()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/CustomSelect/use-select-input.ts` (287 lines)

**Exports:**
- `UseSelectProps`
- `useSelectInput`

**Dependencies:** `react`, `../../context/overlayContext`, `../../ink/events/input-event`, `../../ink`, `../../keybindings/useKeybinding`, `./select`, `./use-select-state`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/CustomSelect/use-select-navigation.ts` (653 lines)

**Exports:**
- `UseSelectNavigationProps`
- `SelectNavigation`
- `useSelectNavigation()`

**Dependencies:** `util`, `./option-map`, `./select`

**Main flow:** Entry: `useSelectNavigation()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/CustomSelect/use-select-state.ts` (157 lines)

**Exports:**
- `UseSelectStateProps`
- `SelectState`
- `useSelectState()`

**Dependencies:** `react`, `./select`, `./use-select-navigation`

**Main flow:** Entry: `useSelectState()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/DesktopHandoff.tsx` (193 lines)

**Exports:**
- `getDownloadUrl()`
- `DesktopHandoff()`

**Dependencies:** `react/compiler-runtime`, `react`, `../commands`, `../ink`, `../utils/browser`, `../utils/desktopDeepLink`, `../utils/errors`, `../utils/gracefulShutdown`, `../utils/sessionStorage`, `./design-system/LoadingState`

**Main flow:** Entry: `getDownloadUrl()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/DesktopUpsell/DesktopUpsellStartup.tsx` (171 lines)

**Exports:**
- `getDesktopUpsellConfig()`
- `shouldShowDesktopUpsellStartup()`
- `DesktopUpsellStartup()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../services/analytics/growthbook`, `../../services/analytics/index`, `../../utils/config`, `../CustomSelect/select`, `../DesktopHandoff`, `../permissions/PermissionDialog`

**Main flow:** Entry: `getDesktopUpsellConfig()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/DevBar.tsx` (49 lines)

**Exports:**
- `DevBar()`

**Dependencies:** `react/compiler-runtime`, `react`, `../bootstrap/state`, `../ink`

**Main flow:** Entry: `DevBar()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/DevChannelsDialog.tsx` (105 lines)

**Exports:**
- `DevChannelsDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `../bootstrap/state`, `../ink`, `../utils/gracefulShutdown`, `./CustomSelect/index`, `./design-system/Dialog`

**Main flow:** Entry: `DevChannelsDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/DiagnosticsDisplay.tsx` (95 lines)

**Exports:**
- `DiagnosticsDisplay()`

**Dependencies:** `react/compiler-runtime`, `path`, `react`, `../ink`, `../services/diagnosticTracking`, `../utils/attachments`, `../utils/cwd`, `./CtrlOToExpand`, `./MessageResponse`

**Main flow:** Entry: `DiagnosticsDisplay()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/EffortCallout.tsx` (265 lines)

**Exports:**
- `EffortCallout()`
- `shouldShowEffortCallout()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `../utils/auth`, `../utils/config`, `../utils/effort`, `../utils/model/model`, `../utils/settings/settings`, `./CustomSelect/select`

**Main flow:** Entry: `EffortCallout()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/EffortIndicator.ts` (42 lines)

**Exports:**
- `getEffortNotificationText()`
- `effortLevelToSymbol()`

**Dependencies:** local only

**Main flow:** Entry: `getEffortNotificationText()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ExitFlow.tsx` (48 lines)

**Exports:**
- `ExitFlow()`

**Dependencies:** `react/compiler-runtime`, `lodash-es/sample`, `react`, `../utils/gracefulShutdown`, `./WorktreeExitDialog`

**Main flow:** Entry: `ExitFlow()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ExportDialog.tsx` (128 lines)

**Exports:**
- `ExportDialog()`

**Dependencies:** `path`, `react`, `../hooks/useExitOnCtrlCDWithKeybindings`, `../hooks/useTerminalSize`, `../ink/termio/osc`, `../ink`, `../keybindings/useKeybinding`, `../utils/cwd`, `../utils/slowOperations`, `./ConfigurableShortcutHint`

**Main flow:** Entry: `ExportDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/FallbackToolUseErrorMessage.tsx` (116 lines)

**Exports:**
- `FallbackToolUseErrorMessage()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/messages/messages.mjs`, `react`, `src/components/shell/OutputLine`, `src/utils/messages`, `src/utils/sandbox/sandbox-ui-utils`, `../ink`, `../keybindings/useShortcutDisplay`, `../utils/stringUtils`, `./MessageResponse`

**Main flow:** Entry: `FallbackToolUseErrorMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/FallbackToolUseRejectedMessage.tsx` (16 lines)

**Exports:**
- `FallbackToolUseRejectedMessage()`

**Dependencies:** `react/compiler-runtime`, `react`, `./InterruptedByUser`, `./MessageResponse`

**Main flow:** Entry: `FallbackToolUseRejectedMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/FastIcon.tsx` (46 lines)

**Exports:**
- `FastIcon()`
- `getFastIconString()`

**Dependencies:** `react/compiler-runtime`, `chalk`, `react`, `../constants/figures`, `../ink`, `../utils/config`, `../utils/systemTheme`, `./design-system/color`

**Main flow:** Entry: `FastIcon()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Feedback.tsx` (592 lines)

**Exports:**
- `redactSensitiveInfo()`
- `Feedback()`
- `createGitHubIssueUrl()`

**Dependencies:** `axios`, `fs/promises`, `react`, `src/bootstrap/state`, `src/services/analytics/firstPartyEventLogger`, `src/services/analytics/index`, `src/utils/messages`, `../commands`, `../hooks/useTerminalSize`

**Main flow:** Entry: `redactSensitiveInfo()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/FeedbackSurvey/FeedbackSurvey.tsx` (174 lines)

**Exports:**
- `FeedbackSurvey()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/services/analytics/index`, `../../ink`, `./FeedbackSurveyView`, `./TranscriptSharePrompt`, `./useDebouncedDigitInput`, `./utils`

**Main flow:** Entry: `FeedbackSurvey()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/FeedbackSurvey/FeedbackSurveyView.tsx` (108 lines)

**Exports:**
- `isValidResponseInput`
- `FeedbackSurveyView()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `./useDebouncedDigitInput`, `./utils`

**Main flow:** Entry: `FeedbackSurveyView()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/FeedbackSurvey/TranscriptSharePrompt.tsx` (88 lines)

**Exports:**
- `TranscriptShareResponse`
- `TranscriptSharePrompt()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../constants/figures`, `../../ink`, `./useDebouncedDigitInput`

**Main flow:** Entry: `TranscriptSharePrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/FeedbackSurvey/submitTranscriptShare.ts` (112 lines)

**Exports:**
- `TranscriptShareTrigger`
- `submitTranscriptShare()`

**Dependencies:** `axios`, `fs/promises`, `../../types/message`, `../../utils/auth`, `../../utils/debug`, `../../utils/errors`, `../../utils/http`, `../../utils/messages`, `../../utils/slowOperations`, `../Feedback`

**Main flow:** Entry: `submitTranscriptShare()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/FeedbackSurvey/useDebouncedDigitInput.ts` (82 lines)

**Exports:**
- `useDebouncedDigitInput()`

**Dependencies:** `react`, `../../utils/stringUtils`

**Main flow:** Entry: `useDebouncedDigitInput()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/FeedbackSurvey/useFeedbackSurvey.tsx` (296 lines)

**Exports:**
- `useFeedbackSurvey()`

**Dependencies:** `react`, `src/hooks/useDynamicConfig`, `src/services/analytics/config`, `src/services/analytics/index`, `../../services/policyLimits/index`, `../../types/message`, `../../utils/config`, `../../utils/envUtils`, `../../utils/messages`, `../../utils/model/model`

**Main flow:** Entry: `useFeedbackSurvey()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/FeedbackSurvey/useMemorySurvey.tsx` (213 lines)

**Exports:**
- `useMemorySurvey()`

**Dependencies:** `react`, `src/services/analytics/config`, `src/services/analytics/growthbook`, `src/services/analytics/index`, `../../memdir/paths`, `../../services/policyLimits/index`, `../../tools/FileReadTool/prompt`, `../../types/message`, `../../utils/config`, `../../utils/envUtils`

**Main flow:** Entry: `useMemorySurvey()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/FeedbackSurvey/usePostCompactSurvey.tsx` (206 lines)

**Exports:**
- `usePostCompactSurvey()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/services/analytics/config`, `src/services/analytics/growthbook`, `src/services/analytics/index`, `../../services/compact/sessionMemoryCompact`, `../../types/message`, `../../utils/envUtils`, `../../utils/messages`, `../../utils/telemetry/events`

**Main flow:** Entry: `usePostCompactSurvey()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/FeedbackSurvey/useSurveyState.tsx` (100 lines)

**Exports:**
- `useSurveyState()`

**Dependencies:** `crypto`, `react`, `./TranscriptSharePrompt`, `./utils`

**Main flow:** Entry: `useSurveyState()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/FileEditToolDiff.tsx` (181 lines)

**Exports:**
- `FileEditToolDiff()`

**Dependencies:** `react/compiler-runtime`, `diff`, `react`, `../hooks/useTerminalSize`, `../ink`, `../tools/FileEditTool/types`, `../tools/FileEditTool/utils`, `../utils/diff`, `../utils/log`

**Main flow:** Entry: `FileEditToolDiff()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/FileEditToolUpdatedMessage.tsx` (124 lines)

**Exports:**
- `FileEditToolUpdatedMessage()`

**Dependencies:** `react/compiler-runtime`, `diff`, `react`, `../hooks/useTerminalSize`, `../ink`, `../utils/array`, `./MessageResponse`, `./StructuredDiffList`

**Main flow:** Entry: `FileEditToolUpdatedMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/FileEditToolUseRejectedMessage.tsx` (170 lines)

**Exports:**
- `FileEditToolUseRejectedMessage()`

**Dependencies:** `react/compiler-runtime`, `diff`, `path`, `react`, `src/hooks/useTerminalSize`, `src/utils/cwd`, `../ink`, `./HighlightedCode`, `./MessageResponse`, `./StructuredDiffList`

**Main flow:** Entry: `FileEditToolUseRejectedMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/FilePathLink.tsx` (43 lines)

**Exports:**
- `FilePathLink()`

**Dependencies:** `react/compiler-runtime`, `react`, `url`, `../ink/components/Link`

**Main flow:** Entry: `FilePathLink()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/FullscreenLayout.tsx` (637 lines)

**Exports:**
- `ScrollChromeContext`
- `useUnseenDivider()`
- `countUnseenAssistantTurns()`
- `UnseenDivider`
- `computeUnseenDivider()`
- `FullscreenLayout()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `url`, `../context/modalContext`, `../context/promptOverlayContext`, `../hooks/useTerminalSize`, `../ink/components/ScrollBox`, `../ink/instances`, `../ink`

**Main flow:** Entry: `useUnseenDivider()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/GlobalSearchDialog.tsx` (343 lines)

**Exports:**
- `GlobalSearchDialog()`
- `parseRipgrepLine()`

**Dependencies:** `react/compiler-runtime`, `path`, `react`, `../context/overlayContext`, `../hooks/useTerminalSize`, `../ink`, `../services/analytics/index`, `../utils/cwd`, `../utils/editor`

**Main flow:** Entry: `GlobalSearchDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/HelpV2/Commands.tsx` (82 lines)

**Exports:**
- `Commands()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../commands`, `../../ink`, `../../utils/format`, `../CustomSelect/select`, `../design-system/Tabs`

**Main flow:** Entry: `Commands()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/HelpV2/General.tsx` (23 lines)

**Exports:**
- `General()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../PromptInput/PromptInputHelpMenu`

**Main flow:** Entry: `General()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/HelpV2/HelpV2.tsx` (184 lines)

**Exports:**
- `HelpV2()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/hooks/useExitOnCtrlCDWithKeybindings`, `src/keybindings/useShortcutDisplay`, `../../commands`, `../../context/modalContext`, `../../hooks/useTerminalSize`, `../../ink`, `../../keybindings/useKeybinding`, `../design-system/Pane`

**Main flow:** Entry: `HelpV2()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/HighlightedCode.tsx` (190 lines)

**Exports:**
- `HighlightedCode`

**Dependencies:** `react/compiler-runtime`, `react`, `../hooks/useSettings`, `../ink`, `../utils/fullscreen`, `../utils/sliceAnsi`, `../utils/stringUtils`, `./HighlightedCode/Fallback`, `./StructuredDiff/colorDiff`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/HighlightedCode/Fallback.tsx` (193 lines)

**Exports:**
- `HighlightedCodeFallback()`

**Dependencies:** `react/compiler-runtime`, `path`, `react`, `../../ink`, `../../utils/cliHighlight`, `../../utils/debug`, `../../utils/file`, `../../utils/hash`

**Main flow:** Entry: `HighlightedCodeFallback()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/HistorySearchDialog.tsx` (118 lines)

**Exports:**
- `HistorySearchDialog()`

**Dependencies:** `react`, `../context/overlayContext`, `../history`, `../hooks/useTerminalSize`, `../ink/stringWidth`, `../ink/wrapAnsi`, `../ink`, `../services/analytics/index`, `../utils/config`

**Main flow:** Entry: `HistorySearchDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/IdeAutoConnectDialog.tsx` (154 lines)

**Exports:**
- `IdeAutoConnectDialog()`
- `shouldShowAutoConnectDialog()`
- `IdeDisableAutoConnectDialog()`
- `shouldShowDisableAutoConnectDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `../utils/config`, `../utils/ide`, `./CustomSelect/index`, `./design-system/Dialog`

**Main flow:** Entry: `IdeAutoConnectDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/IdeOnboardingDialog.tsx` (167 lines)

**Exports:**
- `IdeOnboardingDialog()`
- `hasIdeOnboardingDialogBeenShown()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/utils/envDynamic`, `../ink`, `../keybindings/useKeybinding`, `../utils/config`, `../utils/env`, `../utils/ide`, `./design-system/Dialog`

**Main flow:** Entry: `IdeOnboardingDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/IdeStatusIndicator.tsx` (58 lines)

**Exports:**
- `IdeStatusIndicator()`

**Dependencies:** `react/compiler-runtime`, `path`, `react`, `../hooks/useIdeConnectionStatus`, `../hooks/useIdeSelection`, `../ink`, `../services/mcp/types`

**Main flow:** Entry: `IdeStatusIndicator()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/IdleReturnDialog.tsx` (118 lines)

**Exports:**
- `IdleReturnDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `../utils/format`, `./CustomSelect/index`, `./design-system/Dialog`

**Main flow:** Entry: `IdleReturnDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/InterruptedByUser.tsx` (15 lines)

**Exports:**
- `InterruptedByUser()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`

**Main flow:** Entry: `InterruptedByUser()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/InvalidConfigDialog.tsx` (156 lines)

**Exports:**
- `showInvalidConfigDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `../keybindings/KeybindingProviderSetup`, `../state/AppState`, `../utils/errors`, `../utils/renderOptions`, `../utils/slowOperations`, `../utils/theme`, `./CustomSelect/index`

**Main flow:** Entry: `showInvalidConfigDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/InvalidSettingsDialog.tsx` (89 lines)

**Exports:**
- `InvalidSettingsDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `../utils/settings/validation`, `./CustomSelect/index`, `./design-system/Dialog`, `./ValidationErrorsList`

**Main flow:** Entry: `InvalidSettingsDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/KeybindingWarnings.tsx` (55 lines)

**Exports:**
- `KeybindingWarnings()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `../keybindings/loadUserBindings`

**Main flow:** Entry: `KeybindingWarnings()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/LanguagePicker.tsx` (86 lines)

**Exports:**
- `LanguagePicker()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../ink`, `../keybindings/useKeybinding`, `./TextInput`

**Main flow:** Entry: `LanguagePicker()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/LogSelector.tsx` (1575 lines)

**Exports:**
- `LogSelectorProps`
- `LogSelector()`

**Dependencies:** `react/compiler-runtime`, `chalk`, `figures`, `fuse`, `react`, `../bootstrap/state`, `../hooks/useExitOnCtrlCDWithKeybindings`, `../hooks/useSearchInput`, `../hooks/useTerminalSize`, `../ink/colorize`

**Main flow:** Entry: `LogSelector()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/LogoV2/AnimatedAsterisk.tsx` (50 lines)

**Exports:**
- `AnimatedAsterisk()`

**Dependencies:** `react`, `../../constants/figures`, `../../ink`, `../../utils/settings/settings`, `../Spinner/utils`

**Main flow:** Entry: `AnimatedAsterisk()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/LogoV2/AnimatedClawd.tsx` (124 lines)

**Exports:**
- `AnimatedClawd()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../utils/settings/settings`, `./Clawd`

**Main flow:** Entry: `AnimatedClawd()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/LogoV2/ChannelsNotice.tsx` (266 lines)

**Exports:**
- `ChannelsNotice()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../bootstrap/state`, `../../ink`, `../../services/mcp/channelAllowlist`, `../../services/mcp/channelNotification`, `../../services/mcp/config`, `../../utils/auth`, `../../utils/plugins/installedPluginsManager`

**Feature gates:** `KAIROS`, `KAIROS_CHANNELS`

**Main flow:** Entry: `ChannelsNotice()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/LogoV2/Clawd.tsx` (240 lines)

**Exports:**
- `ClawdPose`
- `Clawd()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../utils/env`

**Main flow:** Entry: `Clawd()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/LogoV2/CondensedLogo.tsx` (161 lines)

**Exports:**
- `CondensedLogo()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../hooks/useMainLoopModel`, `../../hooks/useTerminalSize`, `../../ink/stringWidth`, `../../ink`, `../../state/AppState`, `../../utils/effort`, `../../utils/format`

**Main flow:** Entry: `CondensedLogo()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/LogoV2/EmergencyTip.tsx` (58 lines)

**Exports:**
- `EmergencyTip()`

**Dependencies:** `react`, `src/ink`, `src/services/analytics/growthbook`, `src/utils/config`

**Main flow:** Entry: `EmergencyTip()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/LogoV2/Feed.tsx` (112 lines)

**Exports:**
- `FeedLine`
- `FeedConfig`
- `calculateFeedWidth()`
- `Feed()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink/stringWidth`, `../../ink`, `../../utils/format`

**Main flow:** Entry: `calculateFeedWidth()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/LogoV2/FeedColumn.tsx` (59 lines)

**Exports:**
- `FeedColumn()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../design-system/Divider`, `./Feed`

**Main flow:** Entry: `FeedColumn()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/LogoV2/GuestPassesUpsell.tsx` (70 lines)

**Exports:**
- `useShowGuestPassesUpsell()`
- `incrementGuestPassesSeenCount()`
- `GuestPassesUpsell()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../services/analytics/index`, `../../services/api/referral`, `../../utils/config`

**Main flow:** Entry: `useShowGuestPassesUpsell()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/LogoV2/LogoV2.tsx` (543 lines)

**Exports:**
- `LogoV2()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../hooks/useTerminalSize`, `../../ink/stringWidth`, `../../utils/logoV2Utils`, `../../utils/format`, `../../utils/file`, `./Clawd`, `./FeedColumn`

**Feature gates:** `KAIROS`, `KAIROS_CHANNELS`

**Main flow:** Entry: `LogoV2()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/LogoV2/Opus1mMergeNotice.tsx` (55 lines)

**Exports:**
- `shouldShowOpus1mMergeNotice()`
- `Opus1mMergeNotice()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../constants/figures`, `../../ink`, `../../utils/config`, `../../utils/model/model`, `./AnimatedAsterisk`

**Main flow:** Entry: `shouldShowOpus1mMergeNotice()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/LogoV2/OverageCreditUpsell.tsx` (166 lines)

**Exports:**
- `isEligibleForOverageCreditGrant()`
- `shouldShowOverageCreditUpsell()`
- `maybeRefreshOverageCreditCache()`
- `useShowOverageCreditUpsell()`
- `incrementOverageCreditUpsellSeenCount()`
- `OverageCreditUpsell()`
- `createOverageCreditFeed()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../services/analytics/index`, `../../services/api/overageCreditGrant`, `../../utils/config`, `../../utils/format`, `./Feed`

**Main flow:** Entry: `isEligibleForOverageCreditGrant()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/LogoV2/VoiceModeNotice.tsx` (68 lines)

**Exports:**
- `VoiceModeNotice()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `react`, `../../ink`, `../../utils/config`, `../../utils/settings/settings`, `../../voice/voiceModeEnabled`, `./AnimatedAsterisk`, `./Opus1mMergeNotice`

**Feature gates:** `VOICE_MODE`

**Main flow:** Entry: `VoiceModeNotice()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/LogoV2/WelcomeV2.tsx` (433 lines)

**Exports:**
- `WelcomeV2()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/ink`, `../../utils/env`

**Main flow:** Entry: `WelcomeV2()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/LogoV2/feedConfigs.tsx` (92 lines)

**Exports:**
- `createRecentActivityFeed()`
- `createWhatsNewFeed()`
- `createProjectOnboardingFeed()`
- `createGuestPassesFeed()`

**Dependencies:** `figures`, `os`, `react`, `../../ink`, `../../projectOnboardingState`, `../../services/api/referral`, `../../types/logs`, `../../utils/cwd`, `../../utils/format`, `./Feed`

**Main flow:** Entry: `createRecentActivityFeed()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/LspRecommendation/LspRecommendationMenu.tsx` (88 lines)

**Exports:**
- `LspRecommendationMenu()`

**Dependencies:** `react`, `../../ink`, `../CustomSelect/select`, `../permissions/PermissionDialog`

**Main flow:** Entry: `LspRecommendationMenu()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/MCPServerApprovalDialog.tsx` (115 lines)

**Exports:**
- `MCPServerApprovalDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/services/analytics/index`, `../utils/settings/settings`, `./CustomSelect/index`, `./design-system/Dialog`, `./MCPServerDialogCopy`

**Main flow:** Entry: `MCPServerApprovalDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/MCPServerDesktopImportDialog.tsx` (203 lines)

**Exports:**
- `MCPServerDesktopImportDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/utils/gracefulShutdown`, `src/utils/process`, `../ink`, `../services/mcp/config`, `../services/mcp/types`, `../utils/stringUtils`, `./ConfigurableShortcutHint`, `./CustomSelect/SelectMulti`

**Main flow:** Entry: `MCPServerDesktopImportDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/MCPServerDialogCopy.tsx` (15 lines)

**Exports:**
- `MCPServerDialogCopy()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`

**Main flow:** Entry: `MCPServerDialogCopy()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/MCPServerMultiselectDialog.tsx` (133 lines)

**Exports:**
- `MCPServerMultiselectDialog()`

**Dependencies:** `react/compiler-runtime`, `lodash-es/partition`, `react`, `src/services/analytics/index`, `../ink`, `../utils/settings/settings`, `./ConfigurableShortcutHint`, `./CustomSelect/SelectMulti`, `./design-system/Byline`, `./design-system/Dialog`

**Main flow:** Entry: `MCPServerMultiselectDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ManagedSettingsSecurityDialog/ManagedSettingsSecurityDialog.tsx` (149 lines)

**Exports:**
- `ManagedSettingsSecurityDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../hooks/useExitOnCtrlCDWithKeybindings`, `../../ink`, `../../keybindings/useKeybinding`, `../../utils/settings/types`, `../CustomSelect/index`, `../permissions/PermissionDialog`, `./utils`

**Main flow:** Entry: `ManagedSettingsSecurityDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ManagedSettingsSecurityDialog/utils.ts` (144 lines)

**Exports:**
- `DangerousSettings`
- `extractDangerousSettings()`
- `hasDangerousSettings()`
- `hasDangerousSettingsChanged()`
- `formatDangerousSettingsList()`

**Dependencies:** `../../utils/settings/types`, `../../utils/slowOperations`

**Main flow:** Entry: `extractDangerousSettings()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Markdown.tsx` (236 lines)

**Exports:**
- `Markdown()`
- `StreamingMarkdown()`

**Dependencies:** `react/compiler-runtime`, `marked`, `react`, `../hooks/useSettings`, `../ink`, `../utils/cliHighlight`, `../utils/hash`, `../utils/markdown`, `../utils/messages`, `./MarkdownTable`

**Main flow:** Entry: `Markdown()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/MarkdownTable.tsx` (322 lines)

**Exports:**
- `MarkdownTable()`

**Dependencies:** `marked`, `react`, `strip-ansi`, `../hooks/useTerminalSize`, `../ink/stringWidth`, `../ink/wrapAnsi`, `../ink`, `../utils/cliHighlight`, `../utils/markdown`

**Main flow:** Entry: `MarkdownTable()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/MemoryUsageIndicator.tsx` (37 lines)

**Exports:**
- `MemoryUsageIndicator()`

**Dependencies:** `react`, `../hooks/useMemoryUsage`, `../ink`, `../utils/format`

**Main flow:** Entry: `MemoryUsageIndicator()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Message.tsx` (627 lines)

**Exports:**
- `Props`
- `hasThinkingContent()`
- `areMessagePropsEqual()`
- `Message`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `@anthropic-ai/sdk/resources/beta/messages/messages.mjs`, `@anthropic-ai/sdk/resources/index.mjs`, `react`, `../commands`, `../hooks/useTerminalSize`, `../ink`, `../Tool`, `../types/connectorText`

**Feature gates:** `CONNECTOR_TEXT`, `HISTORY_SNIP`

**Main flow:** Entry: `hasThinkingContent()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/MessageModel.tsx` (43 lines)

**Exports:**
- `MessageModel()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink/stringWidth`, `../ink`, `../types/message`

**Main flow:** Entry: `MessageModel()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/MessageResponse.tsx` (78 lines)

**Exports:**
- `MessageResponse()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `./design-system/Ratchet`

**Main flow:** Entry: `MessageResponse()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/MessageRow.tsx` (383 lines)

**Exports:**
- `Props`
- `hasContentAfterIndex()`
- `isMessageStreaming()`
- `allToolsResolved()`
- `areMessageRowPropsEqual()`
- `MessageRow`

**Dependencies:** `react/compiler-runtime`, `react`, `../commands`, `../ink`, `../screens/REPL`, `../Tool`, `../types/message`, `../utils/collapseReadSearch`, `../utils/messages`, `./Message`

**Main flow:** Entry: `hasContentAfterIndex()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/MessageSelector.tsx` (831 lines)

**Exports:**
- `MessageSelector()`
- `selectableUserMessagesFilter()`
- `messagesAfterAreOnlySynthetic()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/index.mjs`, `crypto`, `figures`, `react`, `src/services/analytics/index`, `src/state/AppState`, `src/utils/fileHistory`, `src/utils/log`

**Main flow:** Entry: `MessageSelector()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/MessageTimestamp.tsx` (63 lines)

**Exports:**
- `MessageTimestamp()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink/stringWidth`, `../ink`, `../types/message`

**Main flow:** Entry: `MessageTimestamp()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Messages.tsx` (834 lines)

**Exports:**
- `filterForBriefTool()`
- `dropTextInBriefTurns()`
- `SliceAnchor`
- `computeSliceStart()`
- `Messages`
- `shouldRenderStatically()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `chalk`, `crypto`, `react`, `src/utils/set`, `../bootstrap/state`, `../commands`

**Feature gates:** `KAIROS`, `KAIROS_BRIEF`, `PROACTIVE`

**Main flow:** Entry: `filterForBriefTool()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ModelPicker.tsx` (448 lines)

**Exports:**
- `Props`
- `ModelPicker()`

**Dependencies:** `react/compiler-runtime`, `lodash-es/capitalize`, `react`, `src/hooks/useExitOnCtrlCDWithKeybindings`, `src/services/analytics/index`, `src/utils/fastMode`, `../ink`, `../keybindings/useKeybinding`, `../state/AppState`

**Main flow:** Entry: `ModelPicker()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/NativeAutoUpdater.tsx` (193 lines)

**Exports:**
- `NativeAutoUpdater()`

**Dependencies:** `react`, `src/services/analytics/index`, `src/utils/debug`, `src/utils/log`, `usehooks-ts`, `../hooks/useUpdateNotification`, `../ink`, `../utils/autoUpdater`

**Main flow:** Entry: `NativeAutoUpdater()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/NotebookEditToolUseRejectedMessage.tsx` (92 lines)

**Exports:**
- `NotebookEditToolUseRejectedMessage()`

**Dependencies:** `react/compiler-runtime`, `path`, `react`, `src/utils/cwd`, `../ink`, `./HighlightedCode`, `./MessageResponse`

**Main flow:** Entry: `NotebookEditToolUseRejectedMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/OffscreenFreeze.tsx` (44 lines)

**Exports:**
- `OffscreenFreeze()`

**Dependencies:** `react`, `../ink/hooks/use-terminal-viewport`, `../ink`, `./messageActions`

**Main flow:** Entry: `OffscreenFreeze()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Onboarding.tsx` (244 lines)

**Exports:**
- `Onboarding()`
- `SkippableStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/services/analytics/index`, `../commands/terminalSetup/terminalSetup`, `../hooks/useExitOnCtrlCDWithKeybindings`, `../ink`, `../keybindings/useKeybinding`, `../utils/auth`, `../utils/authPortable`, `../utils/config`

**Main flow:** Entry: `Onboarding()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/OutputStylePicker.tsx` (112 lines)

**Exports:**
- `OutputStylePickerProps`
- `OutputStylePicker()`

**Dependencies:** `react/compiler-runtime`, `react`, `../constants/outputStyles`, `../ink`, `../utils/config`, `../utils/cwd`, `./CustomSelect/select`, `./design-system/Dialog`

**Main flow:** Entry: `OutputStylePicker()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PackageManagerAutoUpdater.tsx` (104 lines)

**Exports:**
- `PackageManagerAutoUpdater()`

**Dependencies:** `react/compiler-runtime`, `react`, `usehooks-ts`, `../ink`, `../utils/autoUpdater`, `../utils/config`, `../utils/debug`, `../utils/nativeInstaller/packageManagers`, `../utils/semver`

**Main flow:** Entry: `PackageManagerAutoUpdater()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Passes/Passes.tsx` (184 lines)

**Exports:**
- `Passes()`

**Dependencies:** `react`, `../../commands`, `../../constants/figures`, `../../hooks/useExitOnCtrlCDWithKeybindings`, `../../ink/termio/osc`, `../../ink`, `../../keybindings/useKeybinding`, `../../services/analytics/index`, `../../services/api/referral`

**Main flow:** Entry: `Passes()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PrBadge.tsx` (97 lines)

**Exports:**
- `PrBadge()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `../utils/ghPrStatus`

**Main flow:** Entry: `PrBadge()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PressEnterToContinue.tsx` (15 lines)

**Exports:**
- `PressEnterToContinue()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`

**Main flow:** Entry: `PressEnterToContinue()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/HistorySearchInput.tsx` (51 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink/stringWidth`, `../../ink`, `../TextInput`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/IssueFlagBanner.tsx` (12 lines)

**Exports:**
- `IssueFlagBanner()`

**Dependencies:** `react`, `../../constants/figures`, `../../ink`

**Main flow:** Entry: `IssueFlagBanner()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/Notifications.tsx` (332 lines)

**Exports:**
- `FOOTER_TEMPORARY_STATUS_TIMEOUT`
- `Notifications()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `react`, `src/context/notifications`, `src/services/analytics/index`, `src/state/AppState`, `../../context/voice`, `../../hooks/useApiKeyVerification`, `../../hooks/useIdeConnectionStatus`

**Feature gates:** `KAIROS`, `KAIROS_BRIEF`, `VOICE_MODE`

**Main flow:** Entry: `Notifications()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/PromptInput.tsx` (2339 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `bun:bundle`, `chalk`, `path`, `react`, `src/context/notifications`, `src/hooks/useCommandQueue`, `src/hooks/useIdeAtMentioned`, `src/services/analytics/index`, `src/state/AppState`

**Feature gates:** `BUDDY`, `HISTORY_PICKER`, `KAIROS`, `KAIROS_BRIEF`, `QUICK_SEARCH`, `TOKEN_BUDGET` (+2 more)

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/PromptInputFooter.tsx` (191 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `bun:bundle`, `react`, `../../bridge/bridgeEnabled`, `../../bridge/bridgeStatusUtil`, `../../context/promptOverlayContext`, `../../hooks/useApiKeyVerification`, `../../hooks/useIdeSelection`, `../../hooks/useSettings`, `../../hooks/useTerminalSize`

**Feature gates:** `BRIDGE_MODE`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/PromptInputFooterLeftSide.tsx` (517 lines)

**Exports:**
- `PromptInputFooterLeftSide()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `../../ink`, `react`, `figures`, `../../types/textInputTypes`, `../../Tool`, `./utils`, `../../keybindings/useShortcutDisplay`

**Feature gates:** `COORDINATOR_MODE`, `KAIROS`, `PROACTIVE`, `VOICE_MODE`

**Main flow:** Entry: `PromptInputFooterLeftSide()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/PromptInputFooterSuggestions.tsx` (293 lines)

**Exports:**
- `SuggestionItem`
- `SuggestionType`
- `OVERLAY_MAX_ITEMS`
- `PromptInputFooterSuggestions()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../hooks/useTerminalSize`, `../../ink/stringWidth`, `../../ink`, `../../utils/format`, `../../utils/theme`

**Main flow:** Entry: `PromptInputFooterSuggestions()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/PromptInputHelpMenu.tsx` (358 lines)

**Exports:**
- `PromptInputHelpMenu()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `react`, `src/ink`, `src/utils/platform`, `../../keybindings/loadUserBindings`, `../../keybindings/useShortcutDisplay`, `../../services/analytics/growthbook`, `../../utils/fastMode`, `./utils`

**Feature gates:** `TERMINAL_PANEL`

**Main flow:** Entry: `PromptInputHelpMenu()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/PromptInputModeIndicator.tsx` (93 lines)

**Exports:**
- `PromptInputModeIndicator()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `src/ink`, `src/tools/AgentTool/agentColorManager`, `src/types/textInputTypes`, `src/utils/teammate`, `src/utils/theme`, `../../utils/agentSwarmsEnabled`

**Main flow:** Entry: `PromptInputModeIndicator()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/PromptInputQueuedCommands.tsx` (117 lines)

**Exports:**
- `PromptInputQueuedCommands`

**Dependencies:** `bun:bundle`, `react`, `src/ink`, `src/state/AppState`, `../../constants/xml`, `../../context/QueuedMessageContext`, `../../hooks/useCommandQueue`, `../../types/textInputTypes`, `../../utils/messageQueueManager`

**Feature gates:** `KAIROS`, `KAIROS_BRIEF`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/PromptInputStashNotice.tsx` (25 lines)

**Exports:**
- `PromptInputStashNotice()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `src/ink`

**Main flow:** Entry: `PromptInputStashNotice()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/SandboxPromptFooterHint.tsx` (64 lines)

**Exports:**
- `SandboxPromptFooterHint()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../keybindings/useShortcutDisplay`, `../../utils/sandbox/sandbox-adapter`

**Main flow:** Entry: `SandboxPromptFooterHint()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/ShimmeredInput.tsx` (143 lines)

**Exports:**
- `HighlightedInput()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../utils/textHighlighting`, `../Spinner/ShimmerChar`

**Main flow:** Entry: `HighlightedInput()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/VoiceIndicator.tsx` (137 lines)

**Exports:**
- `VoiceIndicator()`
- `VoiceWarmupHint()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `react`, `../../hooks/useSettings`, `../../ink`, `../Spinner/utils`

**Feature gates:** `VOICE_MODE`

**Main flow:** Entry: `VoiceIndicator()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/inputModes.ts` (33 lines)

**Exports:**
- `prependModeCharacterToInput()`
- `getModeFromInput()`
- `getValueFromInput()`
- `isInputModeCharacter()`

**Dependencies:** `src/hooks/useArrowKeyHistory`, `src/types/textInputTypes`

**Main flow:** Entry: `prependModeCharacterToInput()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/inputPaste.ts` (90 lines)

**Exports:**
- `maybeTruncateMessageForInput()`
- `maybeTruncateInput()`

**Dependencies:** `src/history`, `src/utils/config`

**Main flow:** Entry: `maybeTruncateMessageForInput()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/useMaybeTruncateInput.ts` (58 lines)

**Exports:**
- `useMaybeTruncateInput()`

**Dependencies:** `react`, `src/utils/config`, `./inputPaste`

**Main flow:** Entry: `useMaybeTruncateInput()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/usePromptInputPlaceholder.ts` (76 lines)

**Exports:**
- `usePromptInputPlaceholder()`

**Dependencies:** `bun:bundle`, `react`, `src/hooks/useCommandQueue`, `src/state/AppState`, `src/utils/config`, `src/utils/exampleCommands`, `src/utils/messageQueueManager`

**Feature gates:** `KAIROS`, `PROACTIVE`

**Main flow:** Entry: `usePromptInputPlaceholder()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/useShowFastIconHint.ts` (31 lines)

**Exports:**
- `useShowFastIconHint()`

**Dependencies:** `react`

**Main flow:** Entry: `useShowFastIconHint()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/useSwarmBanner.ts` (155 lines)

**Exports:**
- `useSwarmBanner()`

**Dependencies:** `react`, `../../state/AppState`, `../../utils/standaloneAgent`, `../../utils/swarm/backends/detection`, `../../utils/swarm/constants`, `../../utils/teammateContext`, `../../utils/theme`

**Main flow:** Entry: `useSwarmBanner()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/PromptInput/utils.ts` (60 lines)

**Exports:**
- `isVimModeEnabled()`
- `getNewlineInstructions()`
- `isNonSpacePrintable()`

**Dependencies:** `../../ink`, `../../utils/config`, `../../utils/env`

**Main flow:** Entry: `isVimModeEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/QuickOpenDialog.tsx` (244 lines)

**Exports:**
- `QuickOpenDialog()`

**Dependencies:** `react/compiler-runtime`, `path`, `react`, `../context/overlayContext`, `../hooks/fileSuggestions`, `../hooks/useTerminalSize`, `../ink`, `../services/analytics/index`, `../utils/cwd`

**Main flow:** Entry: `QuickOpenDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/RemoteCallout.tsx` (76 lines)

**Exports:**
- `RemoteCallout()`
- `shouldShowRemoteCallout()`

**Dependencies:** `react`, `../bridge/bridgeEnabled`, `../ink`, `../utils/auth`, `../utils/config`, `./CustomSelect/select`, `./permissions/PermissionDialog`

**Main flow:** Entry: `RemoteCallout()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/RemoteEnvironmentDialog.tsx` (340 lines)

**Exports:**
- `RemoteEnvironmentDialog()`

**Dependencies:** `react/compiler-runtime`, `chalk`, `figures`, `react`, `../ink`, `../keybindings/useKeybinding`, `../utils/errors`, `../utils/log`, `../utils/settings/constants`

**Main flow:** Entry: `RemoteEnvironmentDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ResumeTask.tsx` (268 lines)

**Exports:**
- `ResumeTask()`

**Dependencies:** `react`, `src/hooks/useTerminalSize`, `src/utils/teleport/api`, `../ink`, `../keybindings/useKeybinding`, `../keybindings/useShortcutDisplay`, `../utils/debug`, `../utils/detectRepository`, `../utils/format`, `./ConfigurableShortcutHint`

**Main flow:** Entry: `ResumeTask()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/SandboxViolationExpandedView.tsx` (99 lines)

**Exports:**
- `SandboxViolationExpandedView()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `../utils/sandbox/sandbox-adapter`, `src/utils/platform`

**Main flow:** Entry: `SandboxViolationExpandedView()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ScrollKeybindingHandler.tsx` (1012 lines)

**Exports:**
- `shouldClearSelectionOnKey()`
- `selectionFocusMoveForKey()`
- `WheelAccelState`
- `computeWheelStep()`
- `readScrollSpeedBase()`
- `initWheelAccel()`
- `ScrollKeybindingHandler()`
- `dragScrollDirection()`
- `jumpBy()`
- `scrollUp()`
- `ModalPagerAction`
- `modalPagerAction()`
- `applyModalPagerAction()`

**Dependencies:** `react`, `../context/notifications`, `../hooks/useCopyOnSelect`, `../ink/components/ScrollBox`, `../ink/hooks/use-selection`, `../ink/selection`, `../ink/terminal`, `../ink/termio/osc`, `../ink`, `../keybindings/useKeybinding`

**Main flow:** Entry: `shouldClearSelectionOnKey()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/SearchBox.tsx` (72 lines)

**Exports:**
- `SearchBox()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`

**Main flow:** Entry: `SearchBox()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/SentryErrorBoundary.ts` (28 lines)

**Exports:**
- `SentryErrorBoundary`

**Dependencies:** `react`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/SessionBackgroundHint.tsx` (108 lines)

**Exports:**
- `SessionBackgroundHint()`

**Dependencies:** `react/compiler-runtime`, `react`, `../hooks/useDoublePress`, `../ink`, `../keybindings/useKeybinding`, `../keybindings/useShortcutDisplay`, `../state/AppState`, `../tasks/LocalShellTask/LocalShellTask`, `../utils/config`

**Main flow:** Entry: `SessionBackgroundHint()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/SessionPreview.tsx` (194 lines)

**Exports:**
- `SessionPreview()`

**Dependencies:** `react/compiler-runtime`, `crypto`, `react`, `../ink`, `../keybindings/useKeybinding`, `../tools`, `../types/logs`, `../utils/format`, `../utils/sessionStorage`, `./ConfigurableShortcutHint`

**Main flow:** Entry: `SessionPreview()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Settings/Config.tsx` (1822 lines)

**Exports:**
- `Config()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `../../ink`, `../../ink/events/keyboard-event`, `react`, `../../keybindings/useKeybinding`, `figures`, `../../utils/config`, `../../utils/authPortable`

**Feature gates:** `BRIDGE_MODE`, `KAIROS`, `KAIROS_BRIEF`, `KAIROS_PUSH_NOTIFICATION`, `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `Config()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Settings/Settings.tsx` (137 lines)

**Exports:**
- `Settings()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../keybindings/useKeybinding`, `../../hooks/useExitOnCtrlCDWithKeybindings`, `../../hooks/useTerminalSize`, `../../context/modalContext`, `../design-system/Pane`, `../design-system/Tabs`, `./Status`

**Main flow:** Entry: `Settings()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Settings/Status.tsx` (241 lines)

**Exports:**
- `buildDiagnostics()`
- `Status()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../bootstrap/state`, `../../commands`, `../../context/modalContext`, `../../ink`, `../../state/AppState`, `../../utils/cwd`

**Main flow:** Entry: `buildDiagnostics()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Settings/Usage.tsx` (377 lines)

**Exports:**
- `Usage()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/commands/extra-usage/index`, `src/cost-tracker`, `src/utils/auth`, `../../hooks/useTerminalSize`, `../../ink`, `../../keybindings/useKeybinding`, `../../services/api/usage`

**Main flow:** Entry: `Usage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ShowInIDEPrompt.tsx` (170 lines)

**Exports:**
- `ShowInIDEPrompt()`

**Dependencies:** `react/compiler-runtime`, `path`, `react`, `../ink`, `../utils/cwd`, `../utils/ide`, `./CustomSelect/index`, `./design-system/Pane`, `./permissions/FilePermissionDialog/permissionOptions`

**Main flow:** Entry: `ShowInIDEPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/SkillImprovementSurvey.tsx` (152 lines)

**Exports:**
- `SkillImprovementSurvey()`

**Dependencies:** `react/compiler-runtime`, `react`, `../constants/figures`, `../ink`, `../utils/hooks/skillImprovement`, `../utils/stringUtils`, `./FeedbackSurvey/FeedbackSurveyView`, `./FeedbackSurvey/utils`

**Main flow:** Entry: `SkillImprovementSurvey()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Spinner.tsx` (562 lines)

**Exports:**
- `SpinnerWithVerb()`
- `BriefIdleStatus()`
- `Spinner()`

**Dependencies:** `react/compiler-runtime`, `../ink`, `react`, `../bridge/bridgeStatusUtil`, `bun:bundle`, `../bootstrap/state`, `../services/analytics/growthbook`, `../utils/envUtils`, `../utils/array`

**Feature gates:** `KAIROS`, `KAIROS_BRIEF`, `TOKEN_BUDGET`

**Main flow:** Entry: `SpinnerWithVerb()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Spinner/FlashingChar.tsx` (61 lines)

**Exports:**
- `FlashingChar()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../utils/theme`, `./utils`

**Main flow:** Entry: `FlashingChar()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Spinner/GlimmerMessage.tsx` (328 lines)

**Exports:**
- `GlimmerMessage()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink/stringWidth`, `../../ink`, `../../utils/intl`, `../../utils/theme`, `./types`, `./utils`

**Main flow:** Entry: `GlimmerMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Spinner/ShimmerChar.tsx` (36 lines)

**Exports:**
- `ShimmerChar()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../utils/theme`

**Main flow:** Entry: `ShimmerChar()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Spinner/SpinnerAnimationRow.tsx` (265 lines)

**Exports:**
- `SpinnerAnimationRowProps`
- `SpinnerAnimationRow()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../ink/stringWidth`, `../../ink`, `../../tasks/InProcessTeammateTask/types`, `../../utils/format`, `../../utils/ink`, `../../utils/theme`

**Main flow:** Entry: `SpinnerAnimationRow()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Spinner/SpinnerGlyph.tsx` (80 lines)

**Exports:**
- `SpinnerGlyph()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../utils/theme`, `./utils`

**Main flow:** Entry: `SpinnerGlyph()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Spinner/TeammateSpinnerLine.tsx` (233 lines)

**Exports:**
- `TeammateSpinnerLine()`

**Dependencies:** `figures`, `lodash-es/sample`, `react`, `../../constants/spinnerVerbs`, `../../constants/turnCompletionVerbs`, `../../hooks/useElapsedTime`, `../../hooks/useTerminalSize`, `../../ink/stringWidth`, `../../ink`

**Main flow:** Entry: `TeammateSpinnerLine()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Spinner/TeammateSpinnerTree.tsx` (272 lines)

**Exports:**
- `TeammateSpinnerTree()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../ink`, `../../state/AppState`, `../../tasks/InProcessTeammateTask/InProcessTeammateTask`, `../../utils/format`, `./TeammateSpinnerLine`, `./teammateSelectHint`

**Main flow:** Entry: `TeammateSpinnerTree()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Spinner/index.ts` (10 lines)

**Exports:**
- (none — internal module)

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Spinner/teammateSelectHint.ts` (1 lines)

**Exports:**
- `TEAMMATE_SELECT_HINT`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Spinner/useShimmerAnimation.ts` (31 lines)

**Exports:**
- `useShimmerAnimation()`

**Dependencies:** `react`, `../../ink/stringWidth`, `../../ink`, `./types`

**Main flow:** Entry: `useShimmerAnimation()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Spinner/useStalledAnimation.ts` (75 lines)

**Exports:**
- `useStalledAnimation()`

**Dependencies:** `react`

**Main flow:** Entry: `useStalledAnimation()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Spinner/utils.ts` (84 lines)

**Exports:**
- `getDefaultCharacters()`
- `interpolateColor()`
- `toRGBColor()`
- `hueToRgb()`
- `parseRGB()`

**Dependencies:** `../../ink/styles`, `./types`

**Main flow:** Entry: `getDefaultCharacters()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/Stats.tsx` (1228 lines)

**Exports:**
- `Stats()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `asciichart`, `chalk`, `figures`, `react`, `strip-ansi`, `../commands`, `../hooks/useTerminalSize`, `../ink/colorize`

**Feature gates:** `SHOT_STATS`

**Main flow:** Entry: `Stats()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/StatusLine.tsx` (324 lines)

**Exports:**
- `statusLineShouldDisplay()`
- `getLastAssistantMessageId()`
- `StatusLine`

**Dependencies:** `bun:bundle`, `react`, `src/services/analytics/index`, `src/state/AppState`, `src/utils/permissions/PermissionMode`, `../bootstrap/state`, `../constants/outputStyles`, `../context/notifications`, `../cost-tracker`

**Feature gates:** `KAIROS`

**Main flow:** Entry: `statusLineShouldDisplay()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/StatusNotices.tsx` (55 lines)

**Exports:**
- `StatusNotices()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `../tools/AgentTool/loadAgentsDir`, `../utils/claudemd`, `../utils/config`, `../utils/statusNoticeDefinitions`

**Main flow:** Entry: `StatusNotices()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/StructuredDiff.tsx` (190 lines)

**Exports:**
- `StructuredDiff`

**Dependencies:** `react/compiler-runtime`, `diff`, `react`, `../hooks/useSettings`, `../ink`, `../utils/fullscreen`, `../utils/sliceAnsi`, `./StructuredDiff/colorDiff`, `./StructuredDiff/Fallback`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/StructuredDiff/Fallback.tsx` (487 lines)

**Exports:**
- `LineObject`
- `StructuredDiffFallback()`
- `transformLinesToObjects()`
- `processAdjacentLines()`
- `calculateWordDiffs()`
- `numberDiffLines()`

**Dependencies:** `react/compiler-runtime`, `diff`, `react`, `src/utils/theme`, `../../ink/stringWidth`, `../../ink`

**Main flow:** Entry: `StructuredDiffFallback()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/StructuredDiff/colorDiff.ts` (37 lines)

**Exports:**
- `ColorModuleUnavailableReason`
- `getColorModuleUnavailableReason()`
- `expectColorDiff()`
- `expectColorFile()`
- `getSyntaxTheme()`

**Dependencies:** `../../utils/envUtils`

**Main flow:** Entry: `getColorModuleUnavailableReason()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/StructuredDiffList.tsx` (30 lines)

**Exports:**
- `StructuredDiffList()`

**Dependencies:** `diff`, `react`, `../ink`, `../utils/array`, `./StructuredDiff`

**Main flow:** Entry: `StructuredDiffList()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/TagTabs.tsx` (139 lines)

**Exports:**
- `TagTabs()`

**Dependencies:** `react`, `../ink/stringWidth`, `../ink`, `../utils/format`

**Main flow:** Entry: `TagTabs()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/TaskListV2.tsx` (378 lines)

**Exports:**
- `TaskListV2()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../hooks/useTerminalSize`, `../ink/stringWidth`, `../ink`, `../state/AppState`, `../tasks/InProcessTeammateTask/types`, `../tools/AgentTool/agentColorManager`, `../utils/agentSwarmsEnabled`

**Main flow:** Entry: `TaskListV2()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/TeammateViewHeader.tsx` (82 lines)

**Exports:**
- `TeammateViewHeader()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `../state/AppState`, `../state/selectors`, `../utils/ink`, `./design-system/KeyboardShortcutHint`, `./OffscreenFreeze`

**Main flow:** Entry: `TeammateViewHeader()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/TeleportError.tsx` (189 lines)

**Exports:**
- `TeleportLocalErrorType`
- `TeleportError()`
- `getTeleportErrors()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/utils/background/remote/preconditions`, `src/utils/gracefulShutdown`, `../ink`, `./ConsoleOAuthFlow`, `./CustomSelect/index`, `./design-system/Dialog`, `./TeleportStash`

**Main flow:** Entry: `TeleportError()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/TeleportProgress.tsx` (140 lines)

**Exports:**
- `TeleportProgress()`
- `teleportWithProgress()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../ink`, `../state/AppState`, `../utils/teleport`

**Main flow:** Entry: `TeleportProgress()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/TeleportRepoMismatchDialog.tsx` (104 lines)

**Exports:**
- `TeleportRepoMismatchDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `../utils/file`, `../utils/githubRepoPathMapping`, `./CustomSelect/index`, `./design-system/Dialog`, `./Spinner`

**Main flow:** Entry: `TeleportRepoMismatchDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/TeleportResumeWrapper.tsx` (167 lines)

**Exports:**
- `TeleportResumeWrapper()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/services/analytics/index`, `src/utils/conversationRecovery`, `src/utils/teleport/api`, `../hooks/useTeleportResume`, `../ink`, `../keybindings/useKeybinding`, `./ResumeTask`, `./Spinner`

**Main flow:** Entry: `TeleportResumeWrapper()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/TeleportStash.tsx` (116 lines)

**Exports:**
- `TeleportStash()`

**Dependencies:** `figures`, `react`, `../ink`, `../utils/debug`, `../utils/git`, `./CustomSelect/index`, `./design-system/Dialog`, `./Spinner`

**Main flow:** Entry: `TeleportStash()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/TextInput.tsx` (124 lines)

**Exports:**
- `Props`
- default `TextInput()`

**Dependencies:** `bun:bundle`, `chalk`, `react`, `../context/voice`, `../hooks/useClipboardImageHint`, `../hooks/useSettings`, `../hooks/useTextInput`, `../ink`, `../types/textInputTypes`, `../utils/envUtils`

**Feature gates:** `VOICE_MODE`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ThemePicker.tsx` (333 lines)

**Exports:**
- `ThemePickerProps`
- `ThemePicker()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `react`, `../hooks/useExitOnCtrlCDWithKeybindings`, `../hooks/useTerminalSize`, `../ink`, `../keybindings/KeybindingContext`, `../keybindings/useKeybinding`, `../keybindings/useShortcutDisplay`, `../state/AppState`

**Feature gates:** `AUTO_THEME`

**Main flow:** Entry: `ThemePicker()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ThinkingToggle.tsx` (153 lines)

**Exports:**
- `Props`
- `ThinkingToggle()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/hooks/useExitOnCtrlCDWithKeybindings`, `../ink`, `../keybindings/useKeybinding`, `./ConfigurableShortcutHint`, `./CustomSelect/index`, `./design-system/Byline`, `./design-system/KeyboardShortcutHint`

**Main flow:** Entry: `ThinkingToggle()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/TokenWarning.tsx` (179 lines)

**Exports:**
- `TokenWarning()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `react`, `../ink`, `../services/analytics/growthbook`, `../services/compact/autoCompact`, `../services/compact/compactWarningHook`, `../utils/model/contextWindowUpgradeCheck`

**Feature gates:** `CONTEXT_COLLAPSE`, `REACTIVE_COMPACT`

**Main flow:** Entry: `TokenWarning()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ToolUseLoader.tsx` (42 lines)

**Exports:**
- `ToolUseLoader()`

**Dependencies:** `react/compiler-runtime`, `react`, `../constants/figures`, `../hooks/useBlink`, `../ink`

**Main flow:** Entry: `ToolUseLoader()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/TrustDialog/TrustDialog.tsx` (290 lines)

**Exports:**
- `TrustDialog()`

**Dependencies:** `react/compiler-runtime`, `os`, `react`, `src/services/analytics/index`, `../../bootstrap/state`, `../../commands`, `../../hooks/useExitOnCtrlCDWithKeybindings`, `../../ink`, `../../keybindings/useKeybinding`, `../../services/mcp/config`

**Main flow:** Entry: `TrustDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/TrustDialog/utils.ts` (245 lines)

**Exports:**
- `getHooksSources()`
- `getBashPermissionSources()`
- `formatListWithAnd()`
- `getOtelHeadersHelperSources()`
- `getApiKeyHelperSources()`
- `getAwsCommandsSources()`
- `getGcpCommandsSources()`
- `getDangerousEnvVarsSources()`

**Dependencies:** `src/utils/permissions/PermissionRule`, `src/utils/settings/settings`, `src/utils/settings/types`, `../../tools/BashTool/toolName`, `../../utils/managedEnvConstants`, `../../utils/permissions/permissionsLoader`

**Main flow:** Entry: `getHooksSources()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ValidationErrorsList.tsx` (148 lines)

**Exports:**
- `ValidationErrorsList()`

**Dependencies:** `react/compiler-runtime`, `lodash-es/setWith`, `react`, `../ink`, `../utils/settings/validation`, `../utils/treeify`

**Main flow:** Entry: `ValidationErrorsList()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/VimTextInput.tsx` (140 lines)

**Exports:**
- `Props`
- default `VimTextInput()`

**Dependencies:** `react/compiler-runtime`, `chalk`, `react`, `../hooks/useClipboardImageHint`, `../hooks/useVimInput`, `../ink`, `../types/textInputTypes`, `../utils/textHighlighting`, `./BaseTextInput`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/VirtualMessageList.tsx` (1082 lines)

**Exports:**
- `StickyPrompt`
- `JumpHandle`
- `VirtualMessageList()`

**Dependencies:** `react/compiler-runtime`, `react`, `../hooks/useVirtualScroll`, `../ink/components/ScrollBox`, `../ink/dom`, `../ink/render-to-screen`, `../ink`, `../types/message`

**Main flow:** Entry: `VirtualMessageList()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/WorkflowMultiselectDialog.tsx` (128 lines)

**Exports:**
- `WorkflowMultiselectDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `../commands/install-github-app/types`, `../hooks/useExitOnCtrlCDWithKeybindings`, `../ink`, `./ConfigurableShortcutHint`, `./CustomSelect/SelectMulti`, `./design-system/Byline`, `./design-system/Dialog`, `./design-system/KeyboardShortcutHint`

**Main flow:** Entry: `WorkflowMultiselectDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/WorktreeExitDialog.tsx` (231 lines)

**Exports:**
- `WorktreeExitDialog()`

**Dependencies:** `react`, `src/commands`, `src/services/analytics/index`, `src/utils/debug`, `../ink`, `../utils/execFileNoThrow`, `../utils/plans`, `../utils/Shell`, `../utils/worktree`, `./CustomSelect/select`

**Main flow:** Entry: `WorktreeExitDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/AgentDetail.tsx` (220 lines)

**Exports:**
- `AgentDetail()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../ink/events/keyboard-event`, `../../ink`, `../../keybindings/useKeybinding`, `../../Tool`, `../../tools/AgentTool/agentColorManager`, `../../tools/AgentTool/agentMemory`, `../../tools/AgentTool/agentToolUtils`

**Main flow:** Entry: `AgentDetail()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/AgentEditor.tsx` (178 lines)

**Exports:**
- `AgentEditor()`

**Dependencies:** `chalk`, `figures`, `react`, `src/state/AppState`, `../../ink/events/keyboard-event`, `../../ink`, `../../keybindings/useKeybinding`, `../../Tool`, `../../tools/AgentTool/agentColorManager`

**Main flow:** Entry: `AgentEditor()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/AgentNavigationFooter.tsx` (26 lines)

**Exports:**
- `AgentNavigationFooter()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../hooks/useExitOnCtrlCDWithKeybindings`, `../../ink`

**Main flow:** Entry: `AgentNavigationFooter()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/AgentsList.tsx` (440 lines)

**Exports:**
- `AgentsList()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `src/utils/settings/constants`, `../../ink/events/keyboard-event`, `../../ink`, `../../tools/AgentTool/agentDisplay`, `../../tools/AgentTool/loadAgentsDir`, `../../utils/array`

**Main flow:** Entry: `AgentsList()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/AgentsMenu.tsx` (800 lines)

**Exports:**
- `AgentsMenu()`

**Dependencies:** `react/compiler-runtime`, `chalk`, `react`, `src/utils/settings/constants`, `../../commands`, `../../hooks/useExitOnCtrlCDWithKeybindings`, `../../hooks/useMergedTools`, `../../ink`, `../../state/AppState`

**Main flow:** Entry: `AgentsMenu()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/ColorPicker.tsx` (112 lines)

**Exports:**
- `ColorPicker()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../ink/events/keyboard-event`, `../../ink`, `../../tools/AgentTool/agentColorManager`, `../../utils/stringUtils`

**Main flow:** Entry: `ColorPicker()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/ModelSelector.tsx` (68 lines)

**Exports:**
- `ModelSelector()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../utils/model/agent`, `../CustomSelect/select`

**Main flow:** Entry: `ModelSelector()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/ToolSelector.tsx` (562 lines)

**Exports:**
- `ToolSelector()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `src/services/mcp/mcpStringUtils`, `src/services/mcp/utils`, `src/Tool`, `src/tools/AgentTool/agentToolUtils`, `src/tools/AgentTool/constants`, `src/tools/BashTool/BashTool`, `src/tools/ExitPlanModeTool/ExitPlanModeV2Tool`

**Main flow:** Entry: `ToolSelector()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/agentFileUtils.ts` (272 lines)

**Exports:**
- `formatAgentAsMarkdown()`
- `getNewAgentFilePath()`
- `getActualAgentFilePath()`
- `getNewRelativeAgentFilePath()`
- `getActualRelativeAgentFilePath()`
- `saveAgentToFile()`
- `updateAgentFile()`
- `deleteAgentFromFile()`

**Dependencies:** `fs/promises`, `path`, `src/utils/settings/constants`, `src/utils/settings/managedPath`, `../../tools/AgentTool/agentMemory`, `../../utils/cwd`, `../../utils/effort`, `../../utils/envUtils`, `../../utils/errors`, `./types`

**Main flow:** Entry: `formatAgentAsMarkdown()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/generateAgent.ts` (197 lines)

**Exports:**
- `generateAgent()`

**Dependencies:** `@anthropic-ai/sdk/resources/index.mjs`, `src/context`, `src/services/api/claude`, `src/Tool`, `src/tools/AgentTool/constants`, `src/utils/api`, `src/utils/model/model`, `../../memdir/paths`, `../../utils/slowOperations`, `../../utils/systemPromptType`

**Main flow:** Entry: `generateAgent()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/new-agent-creation/CreateAgentWizard.tsx` (97 lines)

**Exports:**
- `CreateAgentWizard()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../memdir/paths`, `../../../Tool`, `../../../tools/AgentTool/loadAgentsDir`, `../../wizard/index`, `../../wizard/types`, `./types`, `./wizard-steps/ColorStep`, `./wizard-steps/ConfirmStepWrapper`

**Main flow:** Entry: `CreateAgentWizard()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/new-agent-creation/wizard-steps/ColorStep.tsx` (84 lines)

**Exports:**
- `ColorStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../../ink`, `../../../../keybindings/useKeybinding`, `../../../../tools/AgentTool/agentColorManager`, `../../../ConfigurableShortcutHint`, `../../../design-system/Byline`, `../../../design-system/KeyboardShortcutHint`, `../../../wizard/index`, `../../../wizard/WizardDialogLayout`

**Main flow:** Entry: `ColorStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/new-agent-creation/wizard-steps/ConfirmStep.tsx` (378 lines)

**Exports:**
- `ConfirmStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../../ink/events/keyboard-event`, `../../../../ink`, `../../../../keybindings/useKeybinding`, `../../../../memdir/paths`, `../../../../Tool`, `../../../../tools/AgentTool/agentMemory`, `../../../../tools/AgentTool/loadAgentsDir`, `../../../../utils/format`

**Main flow:** Entry: `ConfirmStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/new-agent-creation/wizard-steps/ConfirmStepWrapper.tsx` (74 lines)

**Exports:**
- `ConfirmStepWrapper()`

**Dependencies:** `chalk`, `react`, `src/services/analytics/index`, `src/state/AppState`, `../../../../Tool`, `../../../../tools/AgentTool/loadAgentsDir`, `../../../../utils/promptEditor`, `../../../wizard/index`, `../../agentFileUtils`

**Main flow:** Entry: `ConfirmStepWrapper()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/new-agent-creation/wizard-steps/DescriptionStep.tsx` (123 lines)

**Exports:**
- `DescriptionStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../../ink`, `../../../../keybindings/useKeybinding`, `../../../../utils/promptEditor`, `../../../ConfigurableShortcutHint`, `../../../design-system/Byline`, `../../../design-system/KeyboardShortcutHint`, `../../../TextInput`, `../../../wizard/index`

**Main flow:** Entry: `DescriptionStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/new-agent-creation/wizard-steps/GenerateStep.tsx` (143 lines)

**Exports:**
- `GenerateStep()`

**Dependencies:** `@anthropic-ai/sdk`, `react`, `../../../../hooks/useMainLoopModel`, `../../../../ink`, `../../../../keybindings/useKeybinding`, `../../../../utils/abortController`, `../../../../utils/promptEditor`, `../../../ConfigurableShortcutHint`, `../../../design-system/Byline`, `../../../Spinner`

**Main flow:** Entry: `GenerateStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/new-agent-creation/wizard-steps/LocationStep.tsx` (80 lines)

**Exports:**
- `LocationStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../../ink`, `../../../../utils/settings/constants`, `../../../ConfigurableShortcutHint`, `../../../CustomSelect/select`, `../../../design-system/Byline`, `../../../design-system/KeyboardShortcutHint`, `../../../wizard/index`, `../../../wizard/WizardDialogLayout`

**Main flow:** Entry: `LocationStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/new-agent-creation/wizard-steps/MemoryStep.tsx` (113 lines)

**Exports:**
- `MemoryStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../../ink`, `../../../../keybindings/useKeybinding`, `../../../../memdir/paths`, `../../../../tools/AgentTool/agentMemory`, `../../../ConfigurableShortcutHint`, `../../../CustomSelect/select`, `../../../design-system/Byline`, `../../../design-system/KeyboardShortcutHint`

**Main flow:** Entry: `MemoryStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/new-agent-creation/wizard-steps/MethodStep.tsx` (80 lines)

**Exports:**
- `MethodStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../../ink`, `../../../ConfigurableShortcutHint`, `../../../CustomSelect/select`, `../../../design-system/Byline`, `../../../design-system/KeyboardShortcutHint`, `../../../wizard/index`, `../../../wizard/WizardDialogLayout`, `../types`

**Main flow:** Entry: `MethodStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/new-agent-creation/wizard-steps/ModelStep.tsx` (52 lines)

**Exports:**
- `ModelStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../ConfigurableShortcutHint`, `../../../design-system/Byline`, `../../../design-system/KeyboardShortcutHint`, `../../../wizard/index`, `../../../wizard/WizardDialogLayout`, `../../ModelSelector`, `../types`

**Main flow:** Entry: `ModelStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/new-agent-creation/wizard-steps/PromptStep.tsx` (128 lines)

**Exports:**
- `PromptStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../../ink`, `../../../../keybindings/useKeybinding`, `../../../../utils/promptEditor`, `../../../ConfigurableShortcutHint`, `../../../design-system/Byline`, `../../../design-system/KeyboardShortcutHint`, `../../../TextInput`, `../../../wizard/index`

**Main flow:** Entry: `PromptStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/new-agent-creation/wizard-steps/ToolsStep.tsx` (61 lines)

**Exports:**
- `ToolsStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../../Tool`, `../../../ConfigurableShortcutHint`, `../../../design-system/Byline`, `../../../design-system/KeyboardShortcutHint`, `../../../wizard/index`, `../../../wizard/WizardDialogLayout`, `../../ToolSelector`, `../types`

**Main flow:** Entry: `ToolsStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/new-agent-creation/wizard-steps/TypeStep.tsx` (103 lines)

**Exports:**
- `TypeStep()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../../ink`, `../../../../keybindings/useKeybinding`, `../../../../tools/AgentTool/loadAgentsDir`, `../../../ConfigurableShortcutHint`, `../../../design-system/Byline`, `../../../design-system/KeyboardShortcutHint`, `../../../TextInput`, `../../../wizard/index`

**Main flow:** Entry: `TypeStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/types.ts` (27 lines)

**Exports:**
- `AGENT_PATHS`
- `ModeState`
- `AgentValidationResult`

**Dependencies:** `src/utils/settings/constants`, `../../tools/AgentTool/loadAgentsDir`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/utils.ts` (18 lines)

**Exports:**
- `getAgentSourceDisplayName()`

**Dependencies:** `lodash-es/capitalize`, `src/utils/settings/constants`

**Main flow:** Entry: `getAgentSourceDisplayName()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/agents/validateAgent.ts` (109 lines)

**Exports:**
- `AgentValidationResult`
- `validateAgentType()`
- `validateAgent()`

**Dependencies:** `../../Tool`, `../../tools/AgentTool/agentToolUtils`, `./utils`

**Main flow:** Entry: `validateAgentType()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/design-system/Byline.tsx` (77 lines)

**Exports:**
- `Byline()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`

**Main flow:** Entry: `Byline()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/design-system/Dialog.tsx` (138 lines)

**Exports:**
- `Dialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../hooks/useExitOnCtrlCDWithKeybindings`, `../../ink`, `../../keybindings/useKeybinding`, `../../utils/theme`, `../ConfigurableShortcutHint`, `./Byline`, `./KeyboardShortcutHint`, `./Pane`

**Main flow:** Entry: `Dialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/design-system/Divider.tsx` (149 lines)

**Exports:**
- `Divider()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../hooks/useTerminalSize`, `../../ink/stringWidth`, `../../ink`, `../../utils/theme`

**Main flow:** Entry: `Divider()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/design-system/FuzzyPicker.tsx` (312 lines)

**Exports:**
- `FuzzyPicker()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../hooks/useSearchInput`, `../../hooks/useTerminalSize`, `../../ink/events/keyboard-event`, `../../ink/layout/geometry`, `../../ink`, `../SearchBox`, `./Byline`

**Main flow:** Entry: `FuzzyPicker()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/design-system/KeyboardShortcutHint.tsx` (81 lines)

**Exports:**
- `KeyboardShortcutHint()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink/components/Text`

**Main flow:** Entry: `KeyboardShortcutHint()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/design-system/ListItem.tsx` (244 lines)

**Exports:**
- `ListItem()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../ink/hooks/use-declared-cursor`, `../../ink`

**Main flow:** Entry: `ListItem()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/design-system/LoadingState.tsx` (94 lines)

**Exports:**
- `LoadingState()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../Spinner`

**Main flow:** Entry: `LoadingState()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/design-system/Pane.tsx` (77 lines)

**Exports:**
- `Pane()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../context/modalContext`, `../../ink`, `../../utils/theme`, `./Divider`

**Main flow:** Entry: `Pane()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/design-system/ProgressBar.tsx` (86 lines)

**Exports:**
- `ProgressBar()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../utils/theme`

**Main flow:** Entry: `ProgressBar()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/design-system/Ratchet.tsx` (80 lines)

**Exports:**
- `Ratchet()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../hooks/useTerminalSize`, `../../ink/hooks/use-terminal-viewport`, `../../ink`

**Main flow:** Entry: `Ratchet()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/design-system/StatusIcon.tsx` (95 lines)

**Exports:**
- `StatusIcon()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../ink`

**Main flow:** Entry: `StatusIcon()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/design-system/Tabs.tsx` (340 lines)

**Exports:**
- `Tabs()`
- `Tab()`
- `useTabsWidth()`
- `useTabHeaderFocus()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../context/modalContext`, `../../hooks/useTerminalSize`, `../../ink/components/ScrollBox`, `../../ink/events/keyboard-event`, `../../ink/stringWidth`, `../../ink`, `../../keybindings/useKeybinding`, `../../utils/theme`

**Main flow:** Entry: `Tabs()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/design-system/ThemeProvider.tsx` (170 lines)

**Exports:**
- `ThemeProvider()`
- `useTheme()`
- `useThemeSetting()`
- `usePreviewTheme()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `react`, `../../ink/hooks/use-stdin`, `../../utils/config`, `../../utils/systemTheme`, `../../utils/theme`

**Feature gates:** `AUTO_THEME`

**Main flow:** Entry: `ThemeProvider()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/design-system/ThemedBox.tsx` (156 lines)

**Exports:**
- `Props`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink/components/Box`, `../../ink/dom`, `../../ink/events/click-event`, `../../ink/events/focus-event`, `../../ink/events/keyboard-event`, `../../ink/styles`, `../../utils/theme`, `./ThemeProvider`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/design-system/ThemedText.tsx` (124 lines)

**Exports:**
- `TextHoverColorContext`
- `Props`
- default `ThemedText()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink/components/Text`, `../../ink/styles`, `../../utils/theme`, `./ThemeProvider`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/design-system/color.ts` (30 lines)

**Exports:**
- `color()`

**Dependencies:** `../../ink/colorize`, `../../ink/styles`, `../../utils/theme`

**Main flow:** Entry: `color()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/diff/DiffDetailView.tsx` (281 lines)

**Exports:**
- `DiffDetailView()`

**Dependencies:** `react/compiler-runtime`, `diff`, `path`, `react`, `../../hooks/useTerminalSize`, `../../ink`, `../../utils/cwd`, `../../utils/file`, `../design-system/Divider`, `../StructuredDiff`

**Main flow:** Entry: `DiffDetailView()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/diff/DiffDialog.tsx` (383 lines)

**Exports:**
- `DiffDialog()`

**Dependencies:** `react/compiler-runtime`, `diff`, `react`, `../../commands`, `../../context/overlayContext`, `../../hooks/useDiffData`, `../../hooks/useTurnDiffs`, `../../ink`, `../../keybindings/useKeybinding`, `../../keybindings/useShortcutDisplay`

**Main flow:** Entry: `DiffDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/diff/DiffFileList.tsx` (292 lines)

**Exports:**
- `DiffFileList()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../hooks/useDiffData`, `../../hooks/useTerminalSize`, `../../ink`, `../../utils/format`, `../../utils/stringUtils`

**Main flow:** Entry: `DiffFileList()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/grove/Grove.tsx` (463 lines)

**Exports:**
- `GroveDecision`
- `GroveDialog()`
- `PrivacySettingsDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/services/analytics/index`, `../../ink`, `../../services/api/grove`, `../CustomSelect/index`, `../design-system/Byline`, `../design-system/Dialog`, `../design-system/KeyboardShortcutHint`

**Main flow:** Entry: `GroveDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/hooks/HooksConfigMenu.tsx` (578 lines)

**Exports:**
- `HooksConfigMenu()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/entrypoints/agentSdkTypes`, `src/state/AppState`, `../../commands`, `../../hooks/useSettingsChange`, `../../ink`, `../../keybindings/useKeybinding`, `../../utils/hooks/hooksConfigManager`

**Main flow:** Entry: `HooksConfigMenu()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/hooks/PromptDialog.tsx` (90 lines)

**Exports:**
- `PromptDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../keybindings/useKeybinding`, `../../types/hooks`, `../CustomSelect/select`, `../permissions/PermissionDialog`

**Main flow:** Entry: `PromptDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/hooks/SelectEventMode.tsx` (127 lines)

**Exports:**
- `SelectEventMode()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `src/entrypoints/agentSdkTypes`, `src/utils/hooks/hooksConfigManager`, `../../ink`, `../../utils/stringUtils`, `../CustomSelect/select`, `../design-system/Dialog`

**Main flow:** Entry: `SelectEventMode()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/hooks/SelectHookMode.tsx` (112 lines)

**Exports:**
- `SelectHookMode()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/entrypoints/agentSdkTypes`, `src/utils/hooks/hooksConfigManager`, `../../ink`, `../../utils/hooks/hooksSettings`, `../CustomSelect/select`, `../design-system/Dialog`

**Main flow:** Entry: `SelectHookMode()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/hooks/SelectMatcherMode.tsx` (144 lines)

**Exports:**
- `SelectMatcherMode()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/entrypoints/agentSdkTypes`, `../../ink`, `../../utils/hooks/hooksSettings`, `../../utils/stringUtils`, `../CustomSelect/select`, `../design-system/Dialog`

**Main flow:** Entry: `SelectMatcherMode()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/hooks/ViewHookMode.tsx` (199 lines)

**Exports:**
- `ViewHookMode()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../utils/hooks/hooksSettings`, `../design-system/Dialog`

**Main flow:** Entry: `ViewHookMode()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/mcp/CapabilitiesSection.tsx` (61 lines)

**Exports:**
- `CapabilitiesSection()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../design-system/Byline`

**Main flow:** Entry: `CapabilitiesSection()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/mcp/ElicitationDialog.tsx` (1169 lines)

**Exports:**
- `ElicitationDialog()`

**Dependencies:** `react/compiler-runtime`, `@modelcontextprotocol/sdk/types`, `figures`, `react`, `../../context/overlayContext`, `../../hooks/useNotifyAfterTimeout`, `../../hooks/useTerminalSize`, `../../ink`, `../../keybindings/useKeybinding`, `../../services/mcp/elicitationHandler`

**Main flow:** Entry: `ElicitationDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/mcp/MCPAgentServerMenu.tsx` (183 lines)

**Exports:**
- `MCPAgentServerMenu()`

**Dependencies:** `figures`, `react`, `../../commands`, `../../ink`, `../../keybindings/useKeybinding`, `../../services/mcp/auth`, `../../utils/stringUtils`, `../ConfigurableShortcutHint`, `../CustomSelect/index`, `../design-system/Byline`

**Main flow:** Entry: `MCPAgentServerMenu()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/mcp/MCPListPanel.tsx` (504 lines)

**Exports:**
- `MCPListPanel()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../commands`, `../../ink`, `../../keybindings/useKeybinding`, `../../services/mcp/types`, `../../services/mcp/utils`, `../../utils/debug`, `../../utils/stringUtils`

**Main flow:** Entry: `MCPListPanel()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/mcp/MCPReconnect.tsx` (167 lines)

**Exports:**
- `MCPReconnect()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../commands`, `../../ink`, `../../services/mcp/MCPConnectionManager`, `../../state/AppState`, `../Spinner`

**Main flow:** Entry: `MCPReconnect()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/mcp/MCPRemoteServerMenu.tsx` (649 lines)

**Exports:**
- `MCPRemoteServerMenu()`

**Dependencies:** `figures`, `react`, `src/services/analytics/index`, `../../commands`, `../../constants/oauth`, `../../hooks/useExitOnCtrlCDWithKeybindings`, `../../hooks/useTerminalSize`, `../../ink/termio/osc`, `../../ink`, `../../keybindings/useKeybinding`

**Main flow:** Entry: `MCPRemoteServerMenu()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/mcp/MCPSettings.tsx` (398 lines)

**Exports:**
- `MCPSettings()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../commands`, `../../services/mcp/auth`, `../../services/mcp/types`, `../../services/mcp/utils`, `../../state/AppState`, `../../utils/sessionIngressAuth`, `./MCPAgentServerMenu`, `./MCPListPanel`

**Main flow:** Entry: `MCPSettings()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/mcp/MCPStdioServerMenu.tsx` (177 lines)

**Exports:**
- `MCPStdioServerMenu()`

**Dependencies:** `figures`, `react`, `../../commands`, `../../hooks/useExitOnCtrlCDWithKeybindings`, `../../ink`, `../../services/mcp/config`, `../../services/mcp/MCPConnectionManager`, `../../services/mcp/utils`, `../../state/AppState`, `../../utils/errors`

**Main flow:** Entry: `MCPStdioServerMenu()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/mcp/MCPToolDetailView.tsx` (212 lines)

**Exports:**
- `MCPToolDetailView()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../services/mcp/mcpStringUtils`, `../../Tool`, `../ConfigurableShortcutHint`, `../design-system/Dialog`, `./types`

**Main flow:** Entry: `MCPToolDetailView()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/mcp/MCPToolListView.tsx` (141 lines)

**Exports:**
- `MCPToolListView()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../services/mcp/mcpStringUtils`, `../../services/mcp/utils`, `../../state/AppState`, `../../Tool`, `../../utils/stringUtils`, `../ConfigurableShortcutHint`, `../CustomSelect/index`

**Main flow:** Entry: `MCPToolListView()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/mcp/McpParsingWarnings.tsx` (213 lines)

**Exports:**
- `McpParsingWarnings()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/services/mcp/config`, `src/services/mcp/types`, `src/services/mcp/utils`, `src/utils/settings/validation`, `../../ink`

**Main flow:** Entry: `McpParsingWarnings()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/mcp/index.ts` (9 lines)

**Exports:**
- (none — internal module)

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/mcp/utils/reconnectHelpers.tsx` (49 lines)

**Exports:**
- `ReconnectResult`
- `handleReconnectResult()`
- `handleReconnectError()`

**Dependencies:** `../../../commands`, `../../../services/mcp/types`, `../../../Tool`

**Main flow:** Entry: `handleReconnectResult()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/memory/MemoryFileSelector.tsx` (438 lines)

**Exports:**
- `MemoryFileSelector()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `chalk`, `fs/promises`, `path`, `react`, `../../bootstrap/state`, `../../hooks/useExitOnCtrlCDWithKeybindings`, `../../ink`

**Feature gates:** `TEAMMEM`

**Main flow:** Entry: `MemoryFileSelector()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/memory/MemoryUpdateNotification.tsx` (45 lines)

**Exports:**
- `getRelativeMemoryPath()`
- `MemoryUpdateNotification()`

**Dependencies:** `react/compiler-runtime`, `os`, `path`, `react`, `../../ink`, `../../utils/cwd`

**Main flow:** Entry: `getRelativeMemoryPath()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messageActions.tsx` (450 lines)

**Exports:**
- `NavigableType`
- `NavigableOf`
- `NavigableMessage`
- `isNavigableMessage()`
- `toolCallOf()`
- `MessageActionCaps`
- `MESSAGE_ACTIONS`
- `MessageActionsState`
- `MessageActionsNav`
- `MessageActionsSelectedContext`
- `InVirtualListContext`
- `useSelectedMessageBg()`
- `useMessageActions()`
- `MessageActionsKeybindings()`
- `MessageActionsBar()`
- `stripSystemReminders()`
- `copyTextOf()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../ink`, `../keybindings/useKeybinding`, `../services/analytics/index`, `../types/message`, `../utils/messages`

**Main flow:** Entry: `isNavigableMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/AdvisorMessage.tsx` (158 lines)

**Exports:**
- `AdvisorMessage()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../ink`, `../../utils/advisor`, `../../utils/model/model`, `../../utils/slowOperations`, `../CtrlOToExpand`, `../MessageResponse`, `../ToolUseLoader`

**Main flow:** Entry: `AdvisorMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/AssistantRedactedThinkingMessage.tsx` (31 lines)

**Exports:**
- `AssistantRedactedThinkingMessage()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`

**Main flow:** Entry: `AssistantRedactedThinkingMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/AssistantTextMessage.tsx` (270 lines)

**Exports:**
- `AssistantTextMessage()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/index.mjs`, `react`, `src/services/compact/compact`, `src/services/rateLimitMessages`, `../../constants/figures`, `../../ink`, `../../services/api/errors`, `../../utils/messages`, `../../utils/model/contextWindowUpgradeCheck`

**Main flow:** Entry: `AssistantTextMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/AssistantThinkingMessage.tsx` (86 lines)

**Exports:**
- `AssistantThinkingMessage()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/index.mjs`, `react`, `../../ink`, `../CtrlOToExpand`, `../Markdown`

**Main flow:** Entry: `AssistantThinkingMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/AssistantToolUseMessage.tsx` (368 lines)

**Exports:**
- `AssistantToolUseMessage()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/index.mjs`, `react`, `src/hooks/useTerminalSize`, `src/utils/theme`, `../../commands`, `../../constants/figures`, `../../ink/stringWidth`, `../../ink`, `../../state/AppState`

**Main flow:** Entry: `AssistantToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/AttachmentMessage.tsx` (536 lines)

**Exports:**
- `AttachmentMessage()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `src/utils/attachments`, `./nullRenderingAttachments`, `../../state/AppState`, `src/utils/file`, `src/utils/format`, `../MessageResponse`, `path`

**Feature gates:** `EXPERIMENTAL_SKILL_SEARCH`

**Main flow:** Entry: `AttachmentMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/CollapsedReadSearchContent.tsx` (484 lines)

**Exports:**
- `CollapsedReadSearchContent()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `path`, `react`, `../../hooks/useMinDisplayTime`, `../../ink`, `../../Tool`, `../../tools/REPLTool/primitiveTools`, `../../types/message`, `../../utils/array`

**Feature gates:** `TEAMMEM`

**Main flow:** Entry: `CollapsedReadSearchContent()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/CompactBoundaryMessage.tsx` (18 lines)

**Exports:**
- `CompactBoundaryMessage()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../keybindings/useShortcutDisplay`

**Main flow:** Entry: `CompactBoundaryMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/GroupedToolUseContent.tsx` (58 lines)

**Exports:**
- `GroupedToolUseContent()`

**Dependencies:** `@anthropic-ai/sdk/resources/messages/messages.mjs`, `react`, `../../Tool`, `../../types/message`, `../../utils/messages`

**Main flow:** Entry: `GroupedToolUseContent()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/HighlightedThinkingText.tsx` (162 lines)

**Exports:**
- `HighlightedThinkingText()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../context/QueuedMessageContext`, `../../ink`, `../../utils/formatBriefTimestamp`, `../../utils/thinking`, `../messageActions`

**Main flow:** Entry: `HighlightedThinkingText()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/HookProgressMessage.tsx` (116 lines)

**Exports:**
- `HookProgressMessage()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/entrypoints/agentSdkTypes`, `src/utils/messages`, `../../ink`, `../MessageResponse`

**Main flow:** Entry: `HookProgressMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/PlanApprovalMessage.tsx` (222 lines)

**Exports:**
- `PlanApprovalRequestDisplay()`
- `PlanApprovalResponseDisplay()`
- `tryRenderPlanApprovalMessage()`
- `formatTeammateMessageContent()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../components/Markdown`, `../../ink`, `../../utils/slowOperations`, `../../utils/teammateMailbox`, `./ShutdownMessage`, `./TaskAssignmentMessage`

**Main flow:** Entry: `PlanApprovalRequestDisplay()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/RateLimitMessage.tsx` (161 lines)

**Exports:**
- `getUpsellMessage()`
- `RateLimitMessage()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/commands/extra-usage/index`, `src/ink`, `src/services/claudeAiLimitsHook`, `src/services/rateLimitMocking`, `src/utils/auth`, `src/utils/billing`, `../MessageResponse`

**Main flow:** Entry: `getUpsellMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/ShutdownMessage.tsx` (132 lines)

**Exports:**
- `ShutdownRequestDisplay()`
- `ShutdownRejectedDisplay()`
- `tryRenderShutdownMessage()`
- `getShutdownMessageSummary()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../utils/teammateMailbox`

**Main flow:** Entry: `ShutdownRequestDisplay()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/SystemAPIErrorMessage.tsx` (141 lines)

**Exports:**
- `SystemAPIErrorMessage()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/ink`, `src/services/api/errorUtils`, `src/types/message`, `usehooks-ts`, `../CtrlOToExpand`, `../MessageResponse`

**Main flow:** Entry: `SystemAPIErrorMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/SystemTextMessage.tsx` (827 lines)

**Exports:**
- `SystemTextMessage()`

**Dependencies:** `react/compiler-runtime`, `../../ink`, `bun:bundle`, `react`, `lodash-es/sample`, `../../constants/figures`, `figures`, `path`, `../MessageResponse`

**Feature gates:** `TEAMMEM`

**Main flow:** Entry: `SystemTextMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/TaskAssignmentMessage.tsx` (76 lines)

**Exports:**
- `TaskAssignmentDisplay()`
- `tryRenderTaskAssignmentMessage()`
- `getTaskAssignmentSummary()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../utils/teammateMailbox`

**Main flow:** Entry: `TaskAssignmentDisplay()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserAgentNotificationMessage.tsx` (83 lines)

**Exports:**
- `UserAgentNotificationMessage()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/index.mjs`, `react`, `../../constants/figures`, `../../ink`, `../../utils/messages`

**Main flow:** Entry: `UserAgentNotificationMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserBashInputMessage.tsx` (58 lines)

**Exports:**
- `UserBashInputMessage()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/index.mjs`, `react`, `../../ink`, `../../utils/messages`

**Main flow:** Entry: `UserBashInputMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserBashOutputMessage.tsx` (54 lines)

**Exports:**
- `UserBashOutputMessage()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../tools/BashTool/BashToolResultMessage`, `../../utils/messages`

**Main flow:** Entry: `UserBashOutputMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserChannelMessage.tsx` (137 lines)

**Exports:**
- `UserChannelMessage()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/index.mjs`, `react`, `../../constants/figures`, `../../constants/xml`, `../../ink`, `../../utils/format`

**Main flow:** Entry: `UserChannelMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserCommandMessage.tsx` (108 lines)

**Exports:**
- `UserCommandMessage()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/index.mjs`, `figures`, `react`, `../../constants/xml`, `../../ink`, `../../utils/messages`

**Main flow:** Entry: `UserCommandMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserImageMessage.tsx` (59 lines)

**Exports:**
- `UserImageMessage()`

**Dependencies:** `react/compiler-runtime`, `react`, `url`, `../../ink/components/Link`, `../../ink/supports-hyperlinks`, `../../ink`, `../../utils/imageStore`, `../MessageResponse`

**Main flow:** Entry: `UserImageMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserLocalCommandOutputMessage.tsx` (167 lines)

**Exports:**
- `UserLocalCommandOutputMessage()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../constants/figures`, `../../constants/messages`, `../../ink`, `../../utils/messages`, `../Markdown`, `../MessageResponse`

**Main flow:** Entry: `UserLocalCommandOutputMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserMemoryInputMessage.tsx` (75 lines)

**Exports:**
- `UserMemoryInputMessage()`

**Dependencies:** `react/compiler-runtime`, `lodash-es/sample`, `react`, `../../ink`, `../../utils/messages`, `../MessageResponse`

**Main flow:** Entry: `UserMemoryInputMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserPlanMessage.tsx` (42 lines)

**Exports:**
- `UserPlanMessage()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../Markdown`

**Main flow:** Entry: `UserPlanMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserPromptMessage.tsx` (80 lines)

**Exports:**
- `UserPromptMessage()`

**Dependencies:** `bun:bundle`, `@anthropic-ai/sdk/resources/index.mjs`, `react`, `../../bootstrap/state`, `../../ink`, `../../services/analytics/growthbook`, `../../state/AppState`, `../../utils/envUtils`, `../../utils/log`, `../../utils/stringUtils`

**Feature gates:** `KAIROS`, `KAIROS_BRIEF`

**Main flow:** Entry: `UserPromptMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserResourceUpdateMessage.tsx` (121 lines)

**Exports:**
- `UserResourceUpdateMessage()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/index.mjs`, `react`, `../../constants/figures`, `../../ink`

**Main flow:** Entry: `UserResourceUpdateMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserTeammateMessage.tsx` (206 lines)

**Exports:**
- `UserTeammateMessage()`
- `TeammateMessageContent()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/index.mjs`, `figures`, `react`, `../../constants/xml`, `../../ink`, `../../utils/ink`, `../../utils/slowOperations`, `../../utils/teammateMailbox`, `../MessageResponse`

**Main flow:** Entry: `UserTeammateMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserTextMessage.tsx` (275 lines)

**Exports:**
- `UserTextMessage()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `@anthropic-ai/sdk/resources/index.mjs`, `react`, `../../constants/messages`, `../../constants/xml`, `../../utils/agentSwarmsEnabled`, `../../utils/messages`, `../InterruptedByUser`, `../MessageResponse`

**Feature gates:** `FORK_SUBAGENT`, `KAIROS`, `KAIROS_CHANNELS`, `KAIROS_GITHUB_WEBHOOKS`, `UDS_INBOX`

**Main flow:** Entry: `UserTextMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserToolResultMessage/RejectedPlanMessage.tsx` (31 lines)

**Exports:**
- `RejectedPlanMessage()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/components/Markdown`, `src/components/MessageResponse`, `../../../ink`

**Main flow:** Entry: `RejectedPlanMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserToolResultMessage/RejectedToolUseMessage.tsx` (16 lines)

**Exports:**
- `RejectedToolUseMessage()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../ink`, `../../MessageResponse`

**Main flow:** Entry: `RejectedToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserToolResultMessage/UserToolCanceledMessage.tsx` (16 lines)

**Exports:**
- `UserToolCanceledMessage()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/components/InterruptedByUser`, `src/components/MessageResponse`

**Main flow:** Entry: `UserToolCanceledMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserToolResultMessage/UserToolErrorMessage.tsx` (103 lines)

**Exports:**
- `UserToolErrorMessage()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `@anthropic-ai/sdk/resources/index.mjs`, `react`, `../../../constants/figures`, `../../../ink`, `../../../Tool`, `../../../types/message`, `../../../utils/messages`, `../../FallbackToolUseErrorMessage`

**Feature gates:** `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `UserToolErrorMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserToolResultMessage/UserToolRejectMessage.tsx` (95 lines)

**Exports:**
- `UserToolRejectMessage()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../hooks/useTerminalSize`, `../../../ink`, `../../../Tool`, `../../../types/message`, `../../../utils/messages`, `../../FallbackToolUseRejectedMessage`

**Main flow:** Entry: `UserToolRejectMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserToolResultMessage/UserToolResultMessage.tsx` (106 lines)

**Exports:**
- `UserToolResultMessage()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/index.mjs`, `react`, `../../../Tool`, `../../../types/message`, `../../../utils/messages`, `./UserToolCanceledMessage`, `./UserToolErrorMessage`, `./UserToolRejectMessage`, `./UserToolSuccessMessage`

**Main flow:** Entry: `UserToolResultMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserToolResultMessage/UserToolSuccessMessage.tsx` (104 lines)

**Exports:**
- `UserToolSuccessMessage()`

**Dependencies:** `bun:bundle`, `figures`, `react`, `src/components/SentryErrorBoundary`, `../../../ink`, `../../../state/AppState`, `../../../Tool`, `../../../types/message`, `../../../utils/classifierApprovals`, `../../../utils/messages`

**Feature gates:** `BASH_CLASSIFIER`, `KAIROS`, `KAIROS_BRIEF`, `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `UserToolSuccessMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/UserToolResultMessage/utils.tsx` (44 lines)

**Exports:**
- `useGetToolFromMessages()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/index.mjs`, `react`, `../../../Tool`, `../../../utils/messages`

**Main flow:** Entry: `useGetToolFromMessages()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/nullRenderingAttachments.ts` (70 lines)

**Exports:**
- `NullRenderingAttachmentType`
- `isNullRenderingAttachment()`

**Dependencies:** `src/utils/attachments`, `../../types/message`

**Main flow:** Entry: `isNullRenderingAttachment()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/teamMemCollapsed.tsx` (140 lines)

**Exports:**
- `checkHasTeamMemOps()`
- `TeamMemCountParts()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../types/message`

**Feature gates:** `TEAMMEM`

**Main flow:** Entry: `checkHasTeamMemOps()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/messages/teamMemSaved.ts` (19 lines)

**Exports:**
- `teamMemSavedPart()`

**Dependencies:** `../../types/message`

**Feature gates:** `TEAMMEM`

**Main flow:** Entry: `teamMemSavedPart()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/AskUserQuestionPermissionRequest/AskUserQuestionPermissionRequest.tsx` (645 lines)

**Exports:**
- `AskUserQuestionPermissionRequest()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/messages.mjs`, `react`, `../../../hooks/useSettings`, `../../../hooks/useTerminalSize`, `../../../ink/stringWidth`, `../../../ink`, `../../../keybindings/useKeybinding`, `../../../services/analytics/index`, `../../../state/AppState`

**Main flow:** Entry: `AskUserQuestionPermissionRequest()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/AskUserQuestionPermissionRequest/PreviewBox.tsx` (229 lines)

**Exports:**
- `PreviewBox()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../hooks/useSettings`, `../../../hooks/useTerminalSize`, `../../../ink/stringWidth`, `../../../ink`, `../../../utils/cliHighlight`, `../../../utils/markdown`, `../../../utils/sliceAnsi`

**Main flow:** Entry: `PreviewBox()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/AskUserQuestionPermissionRequest/PreviewQuestionView.tsx` (328 lines)

**Exports:**
- `PreviewQuestionView()`

**Dependencies:** `figures`, `react`, `../../../hooks/useTerminalSize`, `../../../ink/events/keyboard-event`, `../../../ink`, `../../../keybindings/useKeybinding`, `../../../state/AppState`, `../../../tools/AskUserQuestionTool/AskUserQuestionTool`, `../../../utils/editor`, `../../../utils/ide`

**Main flow:** Entry: `PreviewQuestionView()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/AskUserQuestionPermissionRequest/QuestionNavigationBar.tsx` (178 lines)

**Exports:**
- `QuestionNavigationBar()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../../hooks/useTerminalSize`, `../../../ink/stringWidth`, `../../../ink`, `../../../tools/AskUserQuestionTool/AskUserQuestionTool`, `../../../utils/format`

**Main flow:** Entry: `QuestionNavigationBar()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/AskUserQuestionPermissionRequest/QuestionView.tsx` (465 lines)

**Exports:**
- `QuestionView()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../../ink/events/keyboard-event`, `../../../ink`, `../../../state/AppState`, `../../../tools/AskUserQuestionTool/AskUserQuestionTool`, `../../../utils/config`, `../../../utils/editor`, `../../../utils/ide`

**Main flow:** Entry: `QuestionView()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/AskUserQuestionPermissionRequest/SubmitQuestionsView.tsx` (144 lines)

**Exports:**
- `SubmitQuestionsView()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../../ink`, `../../../tools/AskUserQuestionTool/AskUserQuestionTool`, `../../../utils/permissions/PermissionResult`, `../../CustomSelect/index`, `../../design-system/Divider`, `../PermissionRequestTitle`, `../PermissionRuleExplanation`

**Main flow:** Entry: `SubmitQuestionsView()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/AskUserQuestionPermissionRequest/use-multiple-choice-state.ts` (179 lines)

**Exports:**
- `AnswerValue`
- `QuestionState`
- `MultipleChoiceState`
- `useMultipleChoiceState()`

**Dependencies:** `react`

**Main flow:** Entry: `useMultipleChoiceState()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/BashPermissionRequest/BashPermissionRequest.tsx` (482 lines)

**Exports:**
- `BashPermissionRequest()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `figures`, `react`, `../../../ink`, `../../../keybindings/useKeybinding`, `../../../services/analytics/growthbook`, `../../../services/analytics/index`, `../../../services/analytics/metadata`, `../../../state/AppState`

**Feature gates:** `BASH_CLASSIFIER`

**Main flow:** Entry: `BashPermissionRequest()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/BashPermissionRequest/bashToolUseOptions.tsx` (147 lines)

**Exports:**
- `BashToolUseOption`
- `bashToolUseOptions()`

**Dependencies:** `../../../tools/BashTool/toolName`, `../../../utils/bash/commands`, `../../../utils/permissions/bashClassifier`, `../../../utils/permissions/PermissionResult`, `../../../utils/permissions/PermissionUpdateSchema`, `../../../utils/permissions/permissionsLoader`, `../../CustomSelect/select`, `../shellPermissionHelpers`

**Main flow:** Entry: `bashToolUseOptions()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/ComputerUseApproval/ComputerUseApproval.tsx` (441 lines)

**Exports:**
- `ComputerUseApproval()`

**Dependencies:** `react/compiler-runtime`, `@ant/computer-use-mcp/sentinelApps`, `@ant/computer-use-mcp/types`, `figures`, `react`, `../../../ink`, `../../../utils/execFileNoThrow`, `../../../utils/stringUtils`

**Main flow:** Entry: `ComputerUseApproval()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/EnterPlanModePermissionRequest/EnterPlanModePermissionRequest.tsx` (122 lines)

**Exports:**
- `EnterPlanModePermissionRequest()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../bootstrap/state`, `../../../ink`, `../../../services/analytics/index`, `../../../state/AppState`, `../../../utils/planModeV2`, `../../CustomSelect/index`, `../PermissionDialog`, `../PermissionRequest`

**Main flow:** Entry: `EnterPlanModePermissionRequest()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/ExitPlanModePermissionRequest/ExitPlanModePermissionRequest.tsx` (768 lines)

**Exports:**
- `buildPermissionUpdates()`
- `autoNameSessionFromPlan()`
- `ExitPlanModePermissionRequest()`
- `buildPlanApprovalOptions()`

**Dependencies:** `bun:bundle`, `crypto`, `figures`, `react`, `src/context/notifications`, `src/services/analytics/index`, `src/state/AppState`, `../../../bootstrap/state`, `../../../commands/rename/generateSessionName`, `../../../commands/ultraplan`

**Feature gates:** `TRANSCRIPT_CLASSIFIER`, `ULTRAPLAN`

**Main flow:** Entry: `buildPermissionUpdates()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/FallbackPermissionRequest.tsx` (333 lines)

**Exports:**
- `FallbackPermissionRequest()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../bootstrap/state`, `../../ink`, `../../services/analytics/metadata`, `../../utils/env`, `../../utils/permissions/permissionsLoader`, `../../utils/stringUtils`, `../../utils/unaryLogging`, `./hooks`

**Main flow:** Entry: `FallbackPermissionRequest()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/FileEditPermissionRequest/FileEditPermissionRequest.tsx` (182 lines)

**Exports:**
- `FileEditPermissionRequest()`

**Dependencies:** `react/compiler-runtime`, `path`, `react`, `src/components/FileEditToolDiff`, `src/utils/cwd`, `zod/v4`, `../../../ink`, `../../../tools/FileEditTool/FileEditTool`, `../FilePermissionDialog/FilePermissionDialog`, `../FilePermissionDialog/ideDiffConfig`

**Main flow:** Entry: `FileEditPermissionRequest()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/FilePermissionDialog/FilePermissionDialog.tsx` (204 lines)

**Exports:**
- `FilePermissionDialogProps`
- `FilePermissionDialog()`

**Dependencies:** `path`, `react`, `../../../hooks/useDiffInIDE`, `../../../ink`, `../../../Tool`, `../../../utils/cliHighlight`, `../../../utils/cwd`, `../../../utils/fsOperations`, `../../../utils/path`, `../../../utils/unaryLogging`

**Main flow:** Entry: `FilePermissionDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/FilePermissionDialog/ideDiffConfig.ts` (42 lines)

**Exports:**
- `FileEdit`
- `IDEDiffConfig`
- `IDEDiffChangeInput`
- `IDEDiffSupport`
- `createSingleEditDiffConfig()`

**Dependencies:** `./useFilePermissionDialog`

**Main flow:** Entry: `createSingleEditDiffConfig()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/FilePermissionDialog/permissionOptions.tsx` (177 lines)

**Exports:**
- `isInClaudeFolder()`
- `isInGlobalClaudeFolder()`
- `PermissionOption`
- `PermissionOptionWithLabel`
- `FileOperationType`
- `getFilePermissionOptions()`

**Dependencies:** `os`, `path`, `react`, `../../../bootstrap/state`, `../../../ink`, `../../../keybindings/shortcutFormat`, `../../../Tool`, `../../../utils/path`, `../../../utils/permissions/filesystem`, `../../CustomSelect/select`

**Main flow:** Entry: `isInClaudeFolder()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/FilePermissionDialog/useFilePermissionDialog.ts` (212 lines)

**Exports:**
- `ToolInput`
- `UseFilePermissionDialogProps`
- `UseFilePermissionDialogResult`
- `useFilePermissionDialog()`

**Dependencies:** `react`, `src/state/AppState`, `../../../keybindings/useKeybinding`, `../../../services/analytics/metadata`, `../../../utils/permissions/PermissionUpdateSchema`, `../../../utils/unaryLogging`, `../PermissionRequest`

**Main flow:** Entry: `useFilePermissionDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/FilePermissionDialog/usePermissionHandler.ts` (185 lines)

**Exports:**
- `PermissionHandlerParams`
- `PermissionHandlerOptions`
- `PERMISSION_HANDLERS`

**Dependencies:** `../../../services/analytics/metadata`, `../../../Tool`, `../../../utils/env`, `../../../utils/permissions/filesystem`, `../../../utils/permissions/PermissionUpdateSchema`, `../PermissionRequest`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/FileWritePermissionRequest/FileWritePermissionRequest.tsx` (161 lines)

**Exports:**
- `FileWritePermissionRequest()`

**Dependencies:** `react/compiler-runtime`, `path`, `react`, `zod/v4`, `../../../ink`, `../../../tools/FileWriteTool/FileWriteTool`, `../../../utils/cwd`, `../../../utils/errors`, `../../../utils/fileRead`, `../FilePermissionDialog/FilePermissionDialog`

**Main flow:** Entry: `FileWritePermissionRequest()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/FileWritePermissionRequest/FileWriteToolDiff.tsx` (89 lines)

**Exports:**
- `FileWriteToolDiff()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../hooks/useTerminalSize`, `../../../ink`, `../../../utils/array`, `../../../utils/diff`, `../../HighlightedCode`, `../../StructuredDiff`

**Main flow:** Entry: `FileWriteToolDiff()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/FilesystemPermissionRequest/FilesystemPermissionRequest.tsx` (115 lines)

**Exports:**
- `FilesystemPermissionRequest()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../ink`, `../FallbackPermissionRequest`, `../FilePermissionDialog/FilePermissionDialog`, `../FilePermissionDialog/useFilePermissionDialog`, `../PermissionRequest`

**Main flow:** Entry: `FilesystemPermissionRequest()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/NotebookEditPermissionRequest/NotebookEditPermissionRequest.tsx` (166 lines)

**Exports:**
- `NotebookEditPermissionRequest()`

**Dependencies:** `react/compiler-runtime`, `path`, `react`, `zod/v4`, `../../../ink`, `../../../tools/NotebookEditTool/NotebookEditTool`, `../../../utils/log`, `../FilePermissionDialog/FilePermissionDialog`, `../PermissionRequest`, `./NotebookEditToolDiff`

**Main flow:** Entry: `NotebookEditPermissionRequest()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/NotebookEditPermissionRequest/NotebookEditToolDiff.tsx` (235 lines)

**Exports:**
- `NotebookEditToolDiff()`

**Dependencies:** `react/compiler-runtime`, `path`, `react`, `../../../ink`, `../../../types/notebook`, `../../../utils/array`, `../../../utils/cwd`, `../../../utils/diff`, `../../../utils/fsOperations`

**Main flow:** Entry: `NotebookEditToolDiff()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/PermissionDecisionDebugInfo.tsx` (460 lines)

**Exports:**
- `PermissionDecisionDebugInfo()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `chalk`, `figures`, `react`, `../../ink`, `../../state/AppState`, `../../utils/permissions/PermissionMode`, `../../utils/permissions/PermissionResult`

**Feature gates:** `BASH_CLASSIFIER`, `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `PermissionDecisionDebugInfo()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/PermissionDialog.tsx` (72 lines)

**Exports:**
- `PermissionDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../utils/theme`, `./PermissionRequestTitle`, `./WorkerBadge`

**Main flow:** Entry: `PermissionDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/PermissionExplanation.tsx` (272 lines)

**Exports:**
- `usePermissionExplainerUI()`
- `PermissionExplainerContent()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../keybindings/useKeybinding`, `../../services/analytics/index`, `../../types/message`, `../../utils/permissions/permissionExplainer`, `../Spinner/ShimmerChar`, `../Spinner/useShimmerAnimation`

**Main flow:** Entry: `usePermissionExplainerUI()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/PermissionPrompt.tsx` (336 lines)

**Exports:**
- `FeedbackType`
- `PermissionPromptOption`
- `ToolAnalyticsContext`
- `PermissionPromptProps`
- `PermissionPrompt()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../keybindings/types`, `../../keybindings/useKeybinding`, `../../services/analytics/index`, `../../state/AppState`, `../CustomSelect/select`

**Main flow:** Entry: `PermissionPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/PermissionRequest.tsx` (217 lines)

**Exports:**
- `PermissionRequestProps`
- `ToolUseConfirm`
- `PermissionRequest()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `react`, `src/tools/EnterPlanModeTool/EnterPlanModeTool`, `src/tools/ExitPlanModeTool/ExitPlanModeV2Tool`, `../../hooks/useNotifyAfterTimeout`, `../../keybindings/useKeybinding`, `../../Tool`, `../../tools/AskUserQuestionTool/AskUserQuestionTool`, `../../tools/BashTool/BashTool`

**Feature gates:** `MONITOR_TOOL`, `REVIEW_ARTIFACT`, `WORKFLOW_SCRIPTS`

**Main flow:** Entry: `PermissionRequest()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/PermissionRequestTitle.tsx` (66 lines)

**Exports:**
- `PermissionRequestTitle()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../utils/theme`, `./WorkerBadge`

**Main flow:** Entry: `PermissionRequestTitle()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/PermissionRuleExplanation.tsx` (121 lines)

**Exports:**
- `PermissionRuleExplanationProps`
- `PermissionRuleExplanation()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `chalk`, `react`, `../../ink`, `../../state/AppState`, `../../utils/permissions/PermissionResult`, `../../utils/permissions/permissionRuleParser`, `../../utils/theme`, `../design-system/ThemedText`

**Feature gates:** `BASH_CLASSIFIER`, `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `PermissionRuleExplanation()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/PowerShellPermissionRequest/PowerShellPermissionRequest.tsx` (235 lines)

**Exports:**
- `PowerShellPermissionRequest()`

**Dependencies:** `react`, `../../../ink`, `../../../keybindings/useKeybinding`, `../../../services/analytics/growthbook`, `../../../services/analytics/index`, `../../../services/analytics/metadata`, `../../../tools/PowerShellTool/destructiveCommandWarning`, `../../../tools/PowerShellTool/PowerShellTool`, `../../../tools/PowerShellTool/readOnlyValidation`, `../../../utils/permissions/PermissionUpdateSchema`

**Main flow:** Entry: `PowerShellPermissionRequest()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/PowerShellPermissionRequest/powershellToolUseOptions.tsx` (91 lines)

**Exports:**
- `PowerShellToolUseOption`
- `powershellToolUseOptions()`

**Dependencies:** `../../../tools/PowerShellTool/toolName`, `../../../utils/permissions/PermissionUpdateSchema`, `../../../utils/permissions/permissionsLoader`, `../../CustomSelect/select`, `../shellPermissionHelpers`

**Main flow:** Entry: `powershellToolUseOptions()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/SandboxPermissionRequest.tsx` (163 lines)

**Exports:**
- `SandboxPermissionRequestProps`
- `SandboxPermissionRequest()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/ink`, `src/utils/sandbox/sandbox-adapter`, `../../services/analytics/index`, `../CustomSelect/select`, `./PermissionDialog`

**Main flow:** Entry: `SandboxPermissionRequest()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/SedEditPermissionRequest/SedEditPermissionRequest.tsx` (230 lines)

**Exports:**
- `SedEditPermissionRequest()`

**Dependencies:** `react/compiler-runtime`, `path`, `react`, `src/components/FileEditToolDiff`, `src/utils/cwd`, `src/utils/errors`, `src/utils/fileRead`, `src/utils/fsOperations`, `../../../ink`, `../../../tools/BashTool/BashTool`

**Main flow:** Entry: `SedEditPermissionRequest()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/SkillPermissionRequest/SkillPermissionRequest.tsx` (369 lines)

**Exports:**
- `SkillPermissionRequest()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/utils/log`, `../../../bootstrap/state`, `../../../ink`, `../../../services/analytics/metadata`, `../../../tools/SkillTool/constants`, `../../../tools/SkillTool/SkillTool`, `../../../utils/env`, `../../../utils/permissions/permissionsLoader`

**Main flow:** Entry: `SkillPermissionRequest()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/WebFetchPermissionRequest/WebFetchPermissionRequest.tsx` (258 lines)

**Exports:**
- `WebFetchPermissionRequest()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../ink`, `../../../tools/WebFetchTool/WebFetchTool`, `../../../utils/permissions/permissionsLoader`, `../../CustomSelect/select`, `../hooks`, `../PermissionDialog`, `../PermissionRequest`, `../PermissionRuleExplanation`

**Main flow:** Entry: `WebFetchPermissionRequest()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/WorkerBadge.tsx` (49 lines)

**Exports:**
- `WorkerBadgeProps`
- `WorkerBadge()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../constants/figures`, `../../ink`, `../../utils/ink`

**Main flow:** Entry: `WorkerBadge()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/WorkerPendingPermission.tsx` (105 lines)

**Exports:**
- `WorkerPendingPermission()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../utils/teammate`, `../Spinner`, `./WorkerBadge`

**Main flow:** Entry: `WorkerPendingPermission()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/hooks.ts` (209 lines)

**Exports:**
- `UnaryEvent`
- `usePermissionRequestLogging()`

**Dependencies:** `bun:bundle`, `react`, `src/services/analytics/metadata`, `src/tools/BashTool/BashTool`, `src/utils/bash/commands`, `src/utils/permissions/permissionRuleParser`, `src/utils/sandbox/sandbox-adapter`, `../../components/permissions/PermissionRequest`, `../../state/AppState`, `../../utils/env`

**Feature gates:** `BASH_CLASSIFIER`, `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `usePermissionRequestLogging()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/rules/AddPermissionRules.tsx` (180 lines)

**Exports:**
- `optionForPermissionSaveDestination()`
- `AddPermissionRules()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../components/CustomSelect/select`, `../../../ink`, `../../../Tool`, `../../../utils/permissions/PermissionRule`, `../../../utils/permissions/PermissionUpdate`, `../../../utils/permissions/permissionRuleParser`, `../../../utils/permissions/shadowedRuleDetection`

**Main flow:** Entry: `optionForPermissionSaveDestination()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/rules/AddWorkspaceDirectory.tsx` (340 lines)

**Exports:**
- `AddWorkspaceDirectory()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `usehooks-ts`, `../../../commands/add-dir/validation`, `../../../components/TextInput`, `../../../ink/events/keyboard-event`, `../../../ink`, `../../../keybindings/useKeybinding`

**Main flow:** Entry: `AddWorkspaceDirectory()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/rules/PermissionRuleDescription.tsx` (76 lines)

**Exports:**
- `PermissionRuleDescription()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../ink`, `../../../tools/BashTool/BashTool`, `../../../utils/permissions/PermissionRule`

**Main flow:** Entry: `PermissionRuleDescription()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/rules/PermissionRuleInput.tsx` (138 lines)

**Exports:**
- `PermissionRuleInputProps`
- `PermissionRuleInput()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../../components/TextInput`, `../../../hooks/useExitOnCtrlCDWithKeybindings`, `../../../hooks/useTerminalSize`, `../../../ink`, `../../../keybindings/useKeybinding`, `../../../tools/BashTool/BashTool`

**Main flow:** Entry: `PermissionRuleInput()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/rules/PermissionRuleList.tsx` (1179 lines)

**Exports:**
- `PermissionRuleList()`

**Dependencies:** `react/compiler-runtime`, `chalk`, `figures`, `react`, `src/state/AppState`, `src/utils/permissions/PermissionUpdate`, `src/utils/permissions/PermissionUpdateSchema`, `../../../commands`, `../../../components/CustomSelect/select`

**Main flow:** Entry: `PermissionRuleList()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/rules/RecentDenialsTab.tsx` (207 lines)

**Exports:**
- `RecentDenialsTab()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../ink`, `../../../utils/autoModeDenials`, `../../CustomSelect/select`, `../../design-system/StatusIcon`, `../../design-system/Tabs`

**Main flow:** Entry: `RecentDenialsTab()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/rules/RemoveWorkspaceDirectory.tsx` (110 lines)

**Exports:**
- `RemoveWorkspaceDirectory()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../../components/CustomSelect/select`, `../../../ink`, `../../../Tool`, `../../../utils/permissions/PermissionUpdate`, `../../design-system/Dialog`

**Main flow:** Entry: `RemoveWorkspaceDirectory()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/rules/WorkspaceTab.tsx` (150 lines)

**Exports:**
- `WorkspaceTab()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../../bootstrap/state`, `../../../commands`, `../../../components/CustomSelect/select`, `../../../ink`, `../../../Tool`, `../../design-system/Tabs`

**Main flow:** Entry: `WorkspaceTab()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/shellPermissionHelpers.tsx` (164 lines)

**Exports:**
- `generateShellSuggestionsLabel()`

**Dependencies:** `path`, `react`, `../../bootstrap/state`, `../../ink`, `../../utils/permissions/PermissionUpdateSchema`, `../../utils/permissions/shellRuleMatching`

**Main flow:** Entry: `generateShellSuggestionsLabel()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/useShellPermissionFeedback.ts` (148 lines)

**Exports:**
- `useShellPermissionFeedback()`

**Dependencies:** `react`, `../../services/analytics/metadata`, `../../state/AppState`, `./PermissionRequest`, `./utils`

**Main flow:** Entry: `useShellPermissionFeedback()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/permissions/utils.ts` (25 lines)

**Exports:**
- `logUnaryPermissionEvent()`

**Dependencies:** `../../utils/env`, `../../utils/unaryLogging`, `./PermissionRequest`

**Main flow:** Entry: `logUnaryPermissionEvent()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/sandbox/SandboxConfigTab.tsx` (45 lines)

**Exports:**
- `SandboxConfigTab()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../utils/sandbox/sandbox-adapter`

**Main flow:** Entry: `SandboxConfigTab()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/sandbox/SandboxDependenciesTab.tsx` (120 lines)

**Exports:**
- `SandboxDependenciesTab()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../utils/platform`, `../../utils/sandbox/sandbox-adapter`

**Main flow:** Entry: `SandboxDependenciesTab()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/sandbox/SandboxDoctorSection.tsx` (46 lines)

**Exports:**
- `SandboxDoctorSection()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../utils/sandbox/sandbox-adapter`

**Main flow:** Entry: `SandboxDoctorSection()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/sandbox/SandboxOverridesTab.tsx` (193 lines)

**Exports:**
- `SandboxOverridesTab()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../types/command`, `../../utils/sandbox/sandbox-adapter`, `../CustomSelect/select`, `../design-system/Tabs`

**Main flow:** Entry: `SandboxOverridesTab()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/sandbox/SandboxSettings.tsx` (296 lines)

**Exports:**
- `SandboxSettings()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../keybindings/useKeybinding`, `../../types/command`, `../../utils/sandbox/sandbox-adapter`, `../../utils/settings/settings`, `../CustomSelect/select`, `../design-system/Pane`

**Main flow:** Entry: `SandboxSettings()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/shell/ExpandShellOutputContext.tsx` (36 lines)

**Exports:**
- `ExpandShellOutputProvider()`
- `useExpandShellOutput()`

**Dependencies:** `react/compiler-runtime`, `react`

**Main flow:** Entry: `ExpandShellOutputProvider()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/shell/OutputLine.tsx` (118 lines)

**Exports:**
- `tryFormatJson()`
- `tryJsonFormatContent()`
- `linkifyUrlsInText()`
- `OutputLine()`
- `stripUnderlineAnsi()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../hooks/useTerminalSize`, `../../ink`, `../../utils/hyperlink`, `../../utils/slowOperations`, `../../utils/terminal`, `../MessageResponse`, `../messageActions`

**Main flow:** Entry: `tryFormatJson()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/shell/ShellProgressMessage.tsx` (150 lines)

**Exports:**
- `ShellProgressMessage()`

**Dependencies:** `react/compiler-runtime`, `react`, `strip-ansi`, `../../ink`, `../../utils/format`, `../MessageResponse`, `../OffscreenFreeze`, `./ShellTimeDisplay`

**Main flow:** Entry: `ShellProgressMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/shell/ShellTimeDisplay.tsx` (74 lines)

**Exports:**
- `ShellTimeDisplay()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../utils/format`

**Main flow:** Entry: `ShellTimeDisplay()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/skills/SkillsMenu.tsx` (237 lines)

**Exports:**
- `SkillsMenu()`

**Dependencies:** `react/compiler-runtime`, `lodash-es/capitalize`, `react`, `../../commands`, `../../ink`, `../../skills/loadSkillsDir`, `../../utils/file`, `../../utils/format`, `../../utils/settings/constants`

**Main flow:** Entry: `SkillsMenu()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/tasks/AsyncAgentDetailDialog.tsx` (229 lines)

**Exports:**
- `AsyncAgentDetailDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/types/utils`, `../../hooks/useElapsedTime`, `../../ink/events/keyboard-event`, `../../ink`, `../../keybindings/useKeybinding`, `../../Tool`, `../../tasks/LocalAgentTask/LocalAgentTask`, `../../tools`

**Main flow:** Entry: `AsyncAgentDetailDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/tasks/BackgroundTask.tsx` (345 lines)

**Exports:**
- `BackgroundTask()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/ink`, `src/tasks/types`, `src/types/utils`, `src/utils/format`, `src/utils/ink`, `src/utils/stringUtils`, `../../constants/figures`, `./RemoteSessionProgress`

**Main flow:** Entry: `BackgroundTask()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/tasks/BackgroundTaskStatus.tsx` (429 lines)

**Exports:**
- `BackgroundTaskStatus()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `src/hooks/useTerminalSize`, `src/ink/stringWidth`, `src/state/AppState`, `src/state/teammateViewHelpers`, `src/tasks/LocalAgentTask/LocalAgentTask`, `src/tasks/pillLabel`

**Main flow:** Entry: `BackgroundTaskStatus()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/tasks/BackgroundTasksDialog.tsx` (652 lines)

**Exports:**
- `BackgroundTasksDialog()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `figures`, `react`, `src/coordinator/coordinatorMode`, `src/hooks/useTerminalSize`, `src/state/AppState`, `src/state/teammateViewHelpers`, `src/Tool`, `src/tasks/DreamTask/DreamTask`

**Feature gates:** `MONITOR_TOOL`, `WORKFLOW_SCRIPTS`

**Main flow:** Entry: `BackgroundTasksDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/tasks/DreamDetailDialog.tsx` (251 lines)

**Exports:**
- `DreamDetailDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/types/utils`, `../../hooks/useElapsedTime`, `../../ink/events/keyboard-event`, `../../ink`, `../../keybindings/useKeybinding`, `../../tasks/DreamTask/DreamTask`, `../../utils/stringUtils`, `../design-system/Byline`

**Main flow:** Entry: `DreamDetailDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/tasks/InProcessTeammateDetailDialog.tsx` (266 lines)

**Exports:**
- `InProcessTeammateDetailDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/types/utils`, `../../hooks/useElapsedTime`, `../../ink/events/keyboard-event`, `../../ink`, `../../keybindings/useKeybinding`, `../../Tool`, `../../tasks/InProcessTeammateTask/types`, `../../tools`

**Main flow:** Entry: `InProcessTeammateDetailDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/tasks/RemoteSessionDetailDialog.tsx` (904 lines)

**Exports:**
- `formatToolUseSummary()`
- `RemoteSessionDetailDialog()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `src/entrypoints/agentSdkTypes`, `src/Tool`, `src/types/utils`, `../../commands`, `../../constants/figures`, `../../hooks/useElapsedTime`, `../../ink/events/keyboard-event`

**Main flow:** Entry: `formatToolUseSummary()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/tasks/RemoteSessionProgress.tsx` (243 lines)

**Exports:**
- `formatReviewStageCounts()`
- `RemoteSessionProgress()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/tasks/RemoteAgentTask/RemoteAgentTask`, `src/types/utils`, `../../constants/figures`, `../../hooks/useSettings`, `../../ink`, `../../utils/array`, `../../utils/thinking`

**Main flow:** Entry: `formatReviewStageCounts()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/tasks/ShellDetailDialog.tsx` (404 lines)

**Exports:**
- `ShellDetailDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/types/utils`, `../../commands`, `../../hooks/useTerminalSize`, `../../ink/events/keyboard-event`, `../../ink`, `../../keybindings/useKeybinding`, `../../tasks/LocalShellTask/guards`, `../../utils/format`

**Main flow:** Entry: `ShellDetailDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/tasks/ShellProgress.tsx` (87 lines)

**Exports:**
- `TaskStatusText()`
- `ShellProgress()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/ink`, `src/Task`, `src/tasks/LocalShellTask/guards`, `src/types/utils`

**Main flow:** Entry: `TaskStatusText()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/tasks/renderToolActivity.tsx` (33 lines)

**Exports:**
- `renderToolActivity()`

**Dependencies:** `react`, `../../ink`, `../../Tool`, `../../tasks/LocalAgentTask/LocalAgentTask`, `../../utils/theme`

**Main flow:** Entry: `renderToolActivity()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/tasks/taskStatusUtils.tsx` (107 lines)

**Exports:**
- `isTerminalStatus()`
- `getTaskStatusIcon()`
- `getTaskStatusColor()`
- `describeTeammateActivity()`
- `shouldHideTasksFooter()`

**Dependencies:** `figures`, `src/Task`, `src/tasks/InProcessTeammateTask/types`, `src/tasks/LocalAgentTask/LocalAgentTask`, `src/tasks/types`, `src/types/utils`, `src/utils/collapseReadSearch`

**Main flow:** Entry: `isTerminalStatus()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/teams/TeamStatus.tsx` (80 lines)

**Exports:**
- `TeamStatus()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `../../state/AppState`

**Main flow:** Entry: `TeamStatus()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/teams/TeamsDialog.tsx` (715 lines)

**Exports:**
- `TeamsDialog()`

**Dependencies:** `react/compiler-runtime`, `crypto`, `figures`, `react`, `usehooks-ts`, `../../context/overlayContext`, `../../ink/stringWidth`, `../../ink`, `../../keybindings/useKeybinding`

**Main flow:** Entry: `TeamsDialog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ui/OrderedList.tsx` (71 lines)

**Exports:**
- `OrderedList`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`, `./OrderedListItem`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ui/OrderedListItem.tsx` (45 lines)

**Exports:**
- `OrderedListItemContext`
- `OrderedListItem()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink`

**Main flow:** Entry: `OrderedListItem()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/ui/TreeSelect.tsx` (397 lines)

**Exports:**
- `TreeNode`
- `TreeSelectProps`
- `TreeSelect()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../ink/events/keyboard-event`, `../../ink`, `../CustomSelect/select`

**Main flow:** Entry: `TreeSelect()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/wizard/WizardDialogLayout.tsx` (65 lines)

**Exports:**
- `WizardDialogLayout()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../utils/theme`, `../design-system/Dialog`, `./useWizard`, `./WizardNavigationFooter`

**Main flow:** Entry: `WizardDialogLayout()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/wizard/WizardNavigationFooter.tsx` (24 lines)

**Exports:**
- `WizardNavigationFooter()`

**Dependencies:** `react`, `../../hooks/useExitOnCtrlCDWithKeybindings`, `../../ink`, `../ConfigurableShortcutHint`, `../design-system/Byline`, `../design-system/KeyboardShortcutHint`

**Main flow:** Entry: `WizardNavigationFooter()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/wizard/WizardProvider.tsx` (213 lines)

**Exports:**
- `WizardContext`
- `WizardProvider()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../hooks/useExitOnCtrlCDWithKeybindings`, `./types`

**Main flow:** Entry: `WizardProvider()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/wizard/index.ts` (9 lines)

**Exports:**
- (none — internal module)

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `components/wizard/useWizard.ts` (13 lines)

**Exports:**
- `useWizard()`

**Dependencies:** `react`, `./types`, `./WizardProvider`

**Main flow:** Entry: `useWizard()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/apiLimits.ts` (94 lines)

**Exports:**
- `API_IMAGE_MAX_BASE64_SIZE`
- `IMAGE_TARGET_RAW_SIZE`
- `IMAGE_MAX_WIDTH`
- `IMAGE_MAX_HEIGHT`
- `PDF_TARGET_RAW_SIZE`
- `API_PDF_MAX_PAGES`
- `PDF_EXTRACT_SIZE_THRESHOLD`
- `PDF_MAX_EXTRACT_SIZE`
- `PDF_MAX_PAGES_PER_READ`
- `PDF_AT_MENTION_INLINE_THRESHOLD`
- `API_MAX_MEDIA_PER_REQUEST`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/betas.ts` (52 lines)

**Exports:**
- `CLAUDE_CODE_20250219_BETA_HEADER`
- `INTERLEAVED_THINKING_BETA_HEADER`
- `CONTEXT_1M_BETA_HEADER`
- `CONTEXT_MANAGEMENT_BETA_HEADER`
- `STRUCTURED_OUTPUTS_BETA_HEADER`
- `WEB_SEARCH_BETA_HEADER`
- `TOOL_SEARCH_BETA_HEADER_1P`
- `TOOL_SEARCH_BETA_HEADER_3P`
- `EFFORT_BETA_HEADER`
- `TASK_BUDGETS_BETA_HEADER`
- `PROMPT_CACHING_SCOPE_BETA_HEADER`
- `FAST_MODE_BETA_HEADER`
- `REDACT_THINKING_BETA_HEADER`
- `TOKEN_EFFICIENT_TOOLS_BETA_HEADER`
- `SUMMARIZE_CONNECTOR_TEXT_BETA_HEADER`
- `AFK_MODE_BETA_HEADER`
- `CLI_INTERNAL_BETA_HEADER`
- `ADVISOR_BETA_HEADER`
- `BEDROCK_EXTRA_PARAMS_HEADERS`
- `VERTEX_COUNT_TOKENS_ALLOWED_BETAS`

**Dependencies:** `bun:bundle`

**Feature gates:** `CONNECTOR_TEXT`, `TRANSCRIPT_CLASSIFIER`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/common.ts` (33 lines)

**Exports:**
- `getLocalISODate()`
- `getSessionStartDate`
- `getLocalMonthYear()`

**Dependencies:** `lodash-es/memoize`

**Main flow:** Entry: `getLocalISODate()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/cyberRiskInstruction.ts` (24 lines)

**Exports:**
- `CYBER_RISK_INSTRUCTION`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/errorIds.ts` (15 lines)

**Exports:**
- `E_TOOL_USE_SUMMARY_GENERATION_FAILED`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/figures.ts` (45 lines)

**Exports:**
- `BLACK_CIRCLE`
- `BULLET_OPERATOR`
- `TEARDROP_ASTERISK`
- `UP_ARROW`
- `DOWN_ARROW`
- `LIGHTNING_BOLT`
- `EFFORT_LOW`
- `EFFORT_MEDIUM`
- `EFFORT_HIGH`
- `EFFORT_MAX`
- `PLAY_ICON`
- `PAUSE_ICON`
- `REFRESH_ARROW`
- `CHANNEL_ARROW`
- `INJECTED_ARROW`
- `FORK_GLYPH`
- `DIAMOND_OPEN`
- `DIAMOND_FILLED`
- `REFERENCE_MARK`
- `FLAG_ICON`
- `BLOCKQUOTE_BAR`
- `HEAVY_HORIZONTAL`
- `BRIDGE_SPINNER_FRAMES`
- `BRIDGE_READY_INDICATOR`
- `BRIDGE_FAILED_INDICATOR`

**Dependencies:** `../utils/env`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/files.ts` (156 lines)

**Exports:**
- `BINARY_EXTENSIONS`
- `hasBinaryExtension()`
- `isBinaryContent()`

**Dependencies:** local only

**Main flow:** Entry: `hasBinaryExtension()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/github-app.ts` (144 lines)

**Exports:**
- `PR_TITLE`
- `GITHUB_ACTION_SETUP_DOCS_URL`
- `WORKFLOW_CONTENT`
- `PR_BODY`
- `CODE_REVIEW_PLUGIN_WORKFLOW_CONTENT`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/keys.ts` (11 lines)

**Exports:**
- `getGrowthBookClientKey()`

**Dependencies:** `../utils/envUtils`

**Main flow:** Entry: `getGrowthBookClientKey()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/messages.ts` (1 lines)

**Exports:**
- `NO_CONTENT_MESSAGE`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/oauth.ts` (234 lines)

**Exports:**
- `fileSuffixForOauthConfig()`
- `CLAUDE_AI_INFERENCE_SCOPE`
- `CLAUDE_AI_PROFILE_SCOPE`
- `OAUTH_BETA_HEADER`
- `CONSOLE_OAUTH_SCOPES`
- `CLAUDE_AI_OAUTH_SCOPES`
- `ALL_OAUTH_SCOPES`
- `MCP_CLIENT_METADATA_URL`
- `getOauthConfig()`

**Dependencies:** `src/utils/envUtils`

**Main flow:** Entry: `fileSuffixForOauthConfig()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/outputStyles.ts` (216 lines)

**Exports:**
- `OutputStyleConfig`
- `OutputStyles`
- `DEFAULT_OUTPUT_STYLE_NAME`
- `OUTPUT_STYLE_CONFIG`
- `getAllOutputStyles`
- `clearAllOutputStylesCache()`
- `getOutputStyleConfig()`
- `hasCustomOutputStyle()`

**Dependencies:** `figures`, `lodash-es/memoize`, `../outputStyles/loadOutputStylesDir`, `../utils/config`, `../utils/cwd`, `../utils/debug`, `../utils/plugins/loadPluginOutputStyles`, `../utils/settings/constants`, `../utils/settings/settings`

**Main flow:** Entry: `clearAllOutputStylesCache()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/product.ts` (76 lines)

**Exports:**
- `PRODUCT_URL`
- `CLAUDE_AI_BASE_URL`
- `CLAUDE_AI_STAGING_BASE_URL`
- `CLAUDE_AI_LOCAL_BASE_URL`
- `isRemoteSessionStaging()`
- `isRemoteSessionLocal()`
- `getClaudeAiBaseUrl()`
- `getRemoteSessionUrl()`

**Dependencies:** local only

**Main flow:** Entry: `isRemoteSessionStaging()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/prompts.ts` (914 lines)

**Exports:**
- `CLAUDE_CODE_DOCS_MAP_URL`
- `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`
- `prependBullets()`
- `getSystemPrompt()`
- `computeEnvInfo()`
- `computeSimpleEnvInfo()`
- `getUnameSR()`
- `DEFAULT_AGENT_PROMPT`
- `enhanceSystemPromptWithEnvDetails()`
- `getScratchpadInstructions()`

**Dependencies:** `os`, `../utils/env`, `../utils/git`, `../utils/cwd`, `../bootstrap/state`, `../utils/worktree`, `./common`, `../utils/settings/settings`, `../tools/FileWriteTool/prompt`, `../tools/FileReadTool/prompt`

**Feature gates:** `CACHED_MICROCOMPACT`, `EXPERIMENTAL_SKILL_SEARCH`, `KAIROS`, `KAIROS_BRIEF`, `PROACTIVE`, `TOKEN_BUDGET` (+1 more)

**Main flow:** Entry: `prependBullets()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/spinnerVerbs.ts` (204 lines)

**Exports:**
- `getSpinnerVerbs()`
- `SPINNER_VERBS`

**Dependencies:** `../utils/settings/settings`

**Main flow:** Entry: `getSpinnerVerbs()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/system.ts` (95 lines)

**Exports:**
- `CLISyspromptPrefix`
- `CLI_SYSPROMPT_PREFIXES`
- `getCLISyspromptPrefix()`
- `getAttributionHeader()`

**Dependencies:** `bun:bundle`, `../services/analytics/growthbook`, `../utils/debug`, `../utils/envUtils`, `../utils/model/providers`, `../utils/workloadContext`

**Feature gates:** `NATIVE_CLIENT_ATTESTATION`

**Main flow:** Entry: `getCLISyspromptPrefix()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/systemPromptSections.ts` (68 lines)

**Exports:**
- `systemPromptSection()`
- `DANGEROUS_uncachedSystemPromptSection()`
- `resolveSystemPromptSections()`
- `clearSystemPromptSections()`

**Dependencies:** local only

**Main flow:** Entry: `systemPromptSection()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/toolLimits.ts` (56 lines)

**Exports:**
- `DEFAULT_MAX_RESULT_SIZE_CHARS`
- `MAX_TOOL_RESULT_TOKENS`
- `BYTES_PER_TOKEN`
- `MAX_TOOL_RESULT_BYTES`
- `MAX_TOOL_RESULTS_PER_MESSAGE_CHARS`
- `TOOL_SUMMARY_MAX_LENGTH`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/tools.ts` (112 lines)

**Exports:**
- `ALL_AGENT_DISALLOWED_TOOLS`
- `CUSTOM_AGENT_DISALLOWED_TOOLS`
- `ASYNC_AGENT_ALLOWED_TOOLS`
- `IN_PROCESS_TEAMMATE_ALLOWED_TOOLS`
- `COORDINATOR_MODE_ALLOWED_TOOLS`

**Dependencies:** `bun:bundle`, `../tools/TaskOutputTool/constants`, `../tools/ExitPlanModeTool/constants`, `../tools/EnterPlanModeTool/constants`, `../tools/AgentTool/constants`, `../tools/AskUserQuestionTool/prompt`, `../tools/TaskStopTool/prompt`, `../tools/FileReadTool/prompt`, `../tools/WebSearchTool/prompt`, `../tools/TodoWriteTool/constants`

**Feature gates:** `AGENT_TRIGGERS`, `WORKFLOW_SCRIPTS`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/turnCompletionVerbs.ts` (12 lines)

**Exports:**
- `TURN_COMPLETION_VERBS`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `constants/xml.ts` (86 lines)

**Exports:**
- `COMMAND_NAME_TAG`
- `COMMAND_MESSAGE_TAG`
- `COMMAND_ARGS_TAG`
- `BASH_INPUT_TAG`
- `BASH_STDOUT_TAG`
- `BASH_STDERR_TAG`
- `LOCAL_COMMAND_STDOUT_TAG`
- `LOCAL_COMMAND_STDERR_TAG`
- `LOCAL_COMMAND_CAVEAT_TAG`
- `TERMINAL_OUTPUT_TAGS`
- `TICK_TAG`
- `TASK_NOTIFICATION_TAG`
- `TASK_ID_TAG`
- `TOOL_USE_ID_TAG`
- `TASK_TYPE_TAG`
- `OUTPUT_FILE_TAG`
- `STATUS_TAG`
- `SUMMARY_TAG`
- `REASON_TAG`
- `WORKTREE_TAG`
- `WORKTREE_PATH_TAG`
- `WORKTREE_BRANCH_TAG`
- `ULTRAPLAN_TAG`
- `REMOTE_REVIEW_TAG`
- `REMOTE_REVIEW_PROGRESS_TAG`
- ... +8 more

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `context.ts` (189 lines)

**Exports:**
- `getSystemPromptInjection()`
- `setSystemPromptInjection()`
- `getGitStatus`
- `getSystemContext`
- `getUserContext`

**Dependencies:** `bun:bundle`, `lodash-es/memoize`, `./constants/common`, `./utils/diagLogs`, `./utils/envUtils`, `./utils/execFileNoThrow`, `./utils/git`, `./utils/gitSettings`, `./utils/log`

**Feature gates:** `BREAK_CACHE_COMMAND`

**Main flow:** Entry: `getSystemPromptInjection()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `context/QueuedMessageContext.tsx` (63 lines)

**Exports:**
- `useQueuedMessage()`
- `QueuedMessageProvider()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`

**Main flow:** Entry: `useQueuedMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `context/fpsMetrics.tsx` (30 lines)

**Exports:**
- `FpsMetricsProvider()`
- `useFpsMetrics()`

**Dependencies:** `react/compiler-runtime`, `react`, `../utils/fpsTracker`

**Main flow:** Entry: `FpsMetricsProvider()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `context/mailbox.tsx` (38 lines)

**Exports:**
- `MailboxProvider()`
- `useMailbox()`

**Dependencies:** `react/compiler-runtime`, `react`, `../utils/mailbox`

**Main flow:** Entry: `MailboxProvider()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `context/modalContext.tsx` (58 lines)

**Exports:**
- `ModalContext`
- `useIsInsideModal()`
- `useModalOrTerminalSize()`
- `useModalScrollRef()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink/components/ScrollBox`

**Main flow:** Entry: `useIsInsideModal()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `context/notifications.tsx` (240 lines)

**Exports:**
- `Notification`
- `useNotifications()`
- `getNext()`

**Dependencies:** `react`, `src/state/AppState`, `../utils/theme`

**Main flow:** Entry: `useNotifications()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `context/overlayContext.tsx` (151 lines)

**Exports:**
- `useRegisterOverlay()`
- `useIsOverlayActive()`
- `useIsModalOverlayActive()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink/instances`, `../state/AppState`

**Main flow:** Entry: `useRegisterOverlay()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `context/promptOverlayContext.tsx` (125 lines)

**Exports:**
- `PromptOverlayData`
- `PromptOverlayProvider()`
- `usePromptOverlay()`
- `usePromptOverlayDialog()`
- `useSetPromptOverlay()`
- `useSetPromptOverlayDialog()`

**Dependencies:** `react/compiler-runtime`, `react`, `../components/PromptInput/PromptInputFooterSuggestions`

**Main flow:** Entry: `PromptOverlayProvider()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `context/stats.tsx` (220 lines)

**Exports:**
- `StatsStore`
- `createStatsStore()`
- `StatsContext`
- `StatsProvider()`
- `useStats()`
- `useCounter()`
- `useGauge()`
- `useTimer()`
- `useSet()`

**Dependencies:** `react/compiler-runtime`, `react`, `../utils/config`

**Main flow:** Entry: `createStatsStore()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `context/voice.tsx` (88 lines)

**Exports:**
- `VoiceState`
- `VoiceProvider()`
- `useVoiceState()`
- `useSetVoiceState()`
- `useGetVoiceState()`

**Dependencies:** `react/compiler-runtime`, `react`, `../state/store`

**Main flow:** Entry: `VoiceProvider()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `cost-tracker.ts` (323 lines)

**Exports:**
- `getStoredSessionCosts()`
- `restoreCostStateForSession()`
- `saveCurrentSessionCosts()`
- `formatTotalCost()`
- `addToTotalSessionCost()`

**Dependencies:** `@anthropic-ai/sdk/resources/beta/messages/messages.mjs`, `chalk`, `./entrypoints/agentSdkTypes`, `./utils/advisor`, `./utils/fastMode`, `./utils/format`, `./utils/fpsTracker`, `./utils/model/model`, `./utils/modelCost`

**Main flow:** Entry: `getStoredSessionCosts()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `history.ts` (464 lines)

**Exports:**
- `getPastedTextRefNumLines()`
- `formatPastedTextRef()`
- `formatImageRef()`
- `parseReferences()`
- `expandPastedTextRefs()`
- `TimestampedHistoryEntry`
- `addToHistory()`
- `clearPendingHistoryEntries()`
- `removeLastFromHistory()`

**Dependencies:** `fs/promises`, `path`, `./bootstrap/state`, `./utils/cleanupRegistry`, `./utils/config`, `./utils/debug`, `./utils/envUtils`, `./utils/errors`, `./utils/fsOperations`, `./utils/lockfile`

**Main flow:** Entry: `getPastedTextRefNumLines()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/fileSuggestions.ts` (811 lines)

**Exports:**
- `onIndexBuildComplete`
- `clearFileSuggestionCaches()`
- `pathListSignature()`
- `getDirectoryNames()`
- `getDirectoryNamesAsync()`
- `getPathsForSuggestions()`
- `findLongestCommonPrefix()`
- `startBackgroundCacheRefresh()`
- `generateFileSuggestions()`
- `applyFileSuggestion()`

**Dependencies:** `fs`, `ignore`, `path`, `../components/PromptInput/PromptInputFooterSuggestions`, `../services/analytics/index`, `../types/fileSuggestion`, `../utils/config`, `../utils/cwd`, `../utils/debug`, `../utils/errors`

**Main flow:** Entry: `clearFileSuggestionCaches()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/notifs/useAutoModeUnavailableNotification.ts` (56 lines)

**Exports:**
- `useAutoModeUnavailableNotification()`

**Dependencies:** `bun:bundle`, `react`, `src/context/notifications`, `../../bootstrap/state`, `../../state/AppState`, `../../utils/permissions/PermissionMode`, `../../utils/settings/settings`

**Feature gates:** `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `useAutoModeUnavailableNotification()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/notifs/useCanSwitchToExistingSubscription.tsx` (60 lines)

**Exports:**
- `useCanSwitchToExistingSubscription()`

**Dependencies:** `react`, `src/services/oauth/getOauthProfile`, `src/utils/auth`, `../../ink`, `../../services/analytics/index`, `../../utils/config`, `./useStartupNotification`

**Main flow:** Entry: `useCanSwitchToExistingSubscription()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/notifs/useDeprecationWarningNotification.tsx` (44 lines)

**Exports:**
- `useDeprecationWarningNotification()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/context/notifications`, `src/utils/model/deprecation`, `../../bootstrap/state`

**Main flow:** Entry: `useDeprecationWarningNotification()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/notifs/useFastModeNotification.tsx` (162 lines)

**Exports:**
- `useFastModeNotification()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/context/notifications`, `src/state/AppState`, `src/utils/fastMode`, `src/utils/format`, `../../bootstrap/state`

**Main flow:** Entry: `useFastModeNotification()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/notifs/useIDEStatusIndicator.tsx` (186 lines)

**Exports:**
- `useIDEStatusIndicator()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/context/notifications`, `src/ink`, `src/services/mcp/types`, `src/utils/config`, `src/utils/ide`, `../../bootstrap/state`, `../useIdeConnectionStatus`, `../useIdeSelection`

**Main flow:** Entry: `useIDEStatusIndicator()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/notifs/useInstallMessages.tsx` (26 lines)

**Exports:**
- `useInstallMessages()`

**Dependencies:** `src/utils/nativeInstaller/index`, `./useStartupNotification`

**Main flow:** Entry: `useInstallMessages()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/notifs/useLspInitializationNotification.tsx` (143 lines)

**Exports:**
- `useLspInitializationNotification()`

**Dependencies:** `react/compiler-runtime`, `react`, `usehooks-ts`, `../../bootstrap/state`, `../../context/notifications`, `../../ink`, `../../services/lsp/manager`, `../../state/AppState`, `../../utils/debug`, `../../utils/envUtils`

**Main flow:** Entry: `useLspInitializationNotification()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/notifs/useMcpConnectivityStatus.tsx` (88 lines)

**Exports:**
- `useMcpConnectivityStatus()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/context/notifications`, `../../bootstrap/state`, `../../ink`, `../../services/mcp/claudeai`, `../../services/mcp/types`

**Main flow:** Entry: `useMcpConnectivityStatus()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/notifs/useModelMigrationNotifications.tsx` (52 lines)

**Exports:**
- `useModelMigrationNotifications()`

**Dependencies:** `src/context/notifications`, `src/utils/config`, `./useStartupNotification`

**Main flow:** Entry: `useModelMigrationNotifications()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/notifs/useNpmDeprecationNotification.tsx` (25 lines)

**Exports:**
- `useNpmDeprecationNotification()`

**Dependencies:** `src/utils/bundledMode`, `src/utils/doctorDiagnostic`, `src/utils/envUtils`, `./useStartupNotification`

**Main flow:** Entry: `useNpmDeprecationNotification()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/notifs/usePluginAutoupdateNotification.tsx` (83 lines)

**Exports:**
- `usePluginAutoupdateNotification()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../bootstrap/state`, `../../context/notifications`, `../../ink`, `../../utils/debug`, `../../utils/plugins/pluginAutoupdate`

**Main flow:** Entry: `usePluginAutoupdateNotification()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/notifs/usePluginInstallationStatus.tsx` (128 lines)

**Exports:**
- `usePluginInstallationStatus()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../bootstrap/state`, `../../context/notifications`, `../../ink`, `../../state/AppState`, `../../utils/debug`, `../../utils/stringUtils`

**Main flow:** Entry: `usePluginInstallationStatus()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/notifs/useRateLimitWarningNotification.tsx` (114 lines)

**Exports:**
- `useRateLimitWarningNotification()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/context/notifications`, `src/ink`, `src/services/claudeAiLimits`, `src/services/claudeAiLimitsHook`, `src/utils/auth`, `src/utils/billing`, `../../bootstrap/state`

**Main flow:** Entry: `useRateLimitWarningNotification()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/notifs/useSettingsErrors.tsx` (69 lines)

**Exports:**
- `useSettingsErrors()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/context/notifications`, `../../bootstrap/state`, `../../utils/settings/allErrors`, `../../utils/settings/validation`, `../useSettingsChange`

**Main flow:** Entry: `useSettingsErrors()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/notifs/useStartupNotification.ts` (41 lines)

**Exports:**
- `useStartupNotification()`

**Dependencies:** `react`, `../../bootstrap/state`, `../../utils/log`

**Main flow:** Entry: `useStartupNotification()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/notifs/useTeammateShutdownNotification.ts` (78 lines)

**Exports:**
- `useTeammateLifecycleNotification()`

**Dependencies:** `react`, `../../bootstrap/state`, `../../state/AppState`, `../../tasks/InProcessTeammateTask/types`

**Main flow:** Entry: `useTeammateLifecycleNotification()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/renderPlaceholder.ts` (51 lines)

**Exports:**
- `renderPlaceholder()`

**Dependencies:** `chalk`

**Main flow:** Entry: `renderPlaceholder()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/toolPermission/PermissionContext.ts` (388 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `bun:bundle`, `@anthropic-ai/sdk/resources/messages.mjs`, `src/services/analytics/metadata`, `../../components/permissions/PermissionRequest`, `../../tools/BashTool/bashPermissions`, `../../tools/BashTool/toolName`, `../../types/message`, `../../utils/classifierApprovals`, `../../utils/debug`, `../../utils/hooks`

**Feature gates:** `BASH_CLASSIFIER`, `TRANSCRIPT_CLASSIFIER`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/toolPermission/handlers/coordinatorHandler.ts` (65 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `bun:bundle`, `../../../types/permissions`, `../../../utils/log`, `../../../utils/permissions/PermissionResult`, `../../../utils/permissions/PermissionUpdateSchema`, `../PermissionContext`

**Feature gates:** `BASH_CLASSIFIER`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/toolPermission/handlers/interactiveHandler.ts` (536 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `bun:bundle`, `@anthropic-ai/sdk/resources/messages.mjs`, `crypto`, `src/utils/debug`, `../../../bootstrap/state`, `../../../bridge/bridgePermissionCallbacks`, `../../../ink/terminal-focus-state`, `../../../services/mcp/channelPermissions`, `../../../tools/BashTool/bashPermissions`, `../../../tools/BashTool/toolName`

**Feature gates:** `BASH_CLASSIFIER`, `KAIROS`, `KAIROS_CHANNELS`, `TRANSCRIPT_CLASSIFIER`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/toolPermission/handlers/swarmWorkerHandler.ts` (159 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `bun:bundle`, `@anthropic-ai/sdk/resources/messages.mjs`, `../../../types/permissions`, `../../../utils/agentSwarmsEnabled`, `../../../utils/errors`, `../../../utils/log`, `../../../utils/permissions/PermissionResult`, `../../../utils/permissions/PermissionUpdateSchema`, `../../useSwarmPermissionPoller`, `../PermissionContext`

**Feature gates:** `BASH_CLASSIFIER`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/toolPermission/permissionLogging.ts` (238 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `bun:bundle`, `src/services/analytics/metadata`, `../../bootstrap/state`, `../../Tool`, `../../utils/cliHighlight`, `../../utils/sandbox/sandbox-adapter`, `../../utils/telemetry/events`

**Feature gates:** `BASH_CLASSIFIER`, `TRANSCRIPT_CLASSIFIER`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/unifiedSuggestions.ts` (202 lines)

**Exports:**
- `generateUnifiedSuggestions()`

**Dependencies:** `fuse`, `path`, `src/components/PromptInput/PromptInputFooterSuggestions`, `src/hooks/fileSuggestions`, `src/services/mcp/types`, `src/tools/AgentTool/agentColorManager`, `src/tools/AgentTool/loadAgentsDir`, `src/utils/format`, `src/utils/log`, `src/utils/theme`

**Main flow:** Entry: `generateUnifiedSuggestions()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useAfterFirstRender.ts` (17 lines)

**Exports:**
- `useAfterFirstRender()`

**Dependencies:** `react`, `../utils/envUtils`

**Main flow:** Entry: `useAfterFirstRender()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useApiKeyVerification.ts` (84 lines)

**Exports:**
- `VerificationStatus`
- `ApiKeyVerificationResult`
- `useApiKeyVerification()`

**Dependencies:** `react`, `../bootstrap/state`, `../services/api/claude`

**Main flow:** Entry: `useApiKeyVerification()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useArrowKeyHistory.tsx` (229 lines)

**Exports:**
- `HistoryMode`
- `useArrowKeyHistory()`

**Dependencies:** `react`, `src/components/PromptInput/inputModes`, `src/context/notifications`, `../components/ConfigurableShortcutHint`, `../components/PromptInput/Notifications`, `../history`, `../ink`, `../types/textInputTypes`, `../utils/config`

**Main flow:** Entry: `useArrowKeyHistory()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useAssistantHistory.ts` (250 lines)

**Exports:**
- `useAssistantHistory()`

**Dependencies:** `crypto`, `../ink/components/ScrollBox`, `../remote/RemoteSessionManager`, `../remote/sdkMessageAdapter`, `../types/message`, `../utils/debug`

**Feature gates:** `KAIROS`

**Main flow:** Entry: `useAssistantHistory()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useAwaySummary.ts` (125 lines)

**Exports:**
- `useAwaySummary()`

**Dependencies:** `bun:bundle`, `react`, `../services/analytics/growthbook`, `../services/awaySummary`, `../types/message`, `../utils/messages`

**Feature gates:** `AWAY_SUMMARY`

**Main flow:** Entry: `useAwaySummary()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useBackgroundTaskNavigation.ts` (251 lines)

**Exports:**
- `useBackgroundTaskNavigation()`

**Dependencies:** `react`, `../ink/events/keyboard-event`, `../ink`, `../tasks/types`

**Main flow:** Entry: `useBackgroundTaskNavigation()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useBlink.ts` (34 lines)

**Exports:**
- `useBlink()`

**Dependencies:** `../ink`

**Main flow:** Entry: `useBlink()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useCanUseTool.tsx` (204 lines)

**Exports:**
- `CanUseToolFn`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `@anthropic-ai/sdk`, `react`, `src/services/analytics/index`, `src/services/analytics/metadata`, `../components/permissions/PermissionRequest`, `../ink`, `../Tool`

**Feature gates:** `BASH_CLASSIFIER`, `BRIDGE_MODE`, `KAIROS`, `KAIROS_CHANNELS`, `TRANSCRIPT_CLASSIFIER`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useCancelRequest.ts` (276 lines)

**Exports:**
- `CancelRequestHandler()`

**Dependencies:** `react`, `src/services/analytics/index`, `src/services/analytics/metadata`, `../components/PromptInput/utils`, `../components/permissions/PermissionRequest`, `../components/Spinner/types`, `../context/notifications`, `../context/overlayContext`, `../hooks/useCommandQueue`, `../keybindings/shortcutFormat`

**Main flow:** Entry: `CancelRequestHandler()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useChromeExtensionNotification.tsx` (50 lines)

**Exports:**
- `useChromeExtensionNotification()`

**Dependencies:** `react`, `../ink`, `../utils/auth`, `../utils/claudeInChrome/setup`, `../utils/envUtils`, `./notifs/useStartupNotification`

**Main flow:** Entry: `useChromeExtensionNotification()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useClaudeCodeHintRecommendation.tsx` (129 lines)

**Exports:**
- `useClaudeCodeHintRecommendation()`

**Dependencies:** `react/compiler-runtime`, `react`, `../context/notifications`, `../services/analytics/index`, `../utils/claudeCodeHints`, `../utils/debug`, `../utils/plugins/hintRecommendation`, `../utils/plugins/pluginInstallationHelpers`, `./usePluginRecommendationBase`

**Main flow:** Entry: `useClaudeCodeHintRecommendation()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useClipboardImageHint.ts` (77 lines)

**Exports:**
- `useClipboardImageHint()`

**Dependencies:** `react`, `../context/notifications`, `../keybindings/shortcutFormat`, `../utils/imagePaste`

**Main flow:** Entry: `useClipboardImageHint()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useCommandKeybindings.tsx` (108 lines)

**Exports:**
- `CommandKeybindingHandlers()`

**Dependencies:** `react/compiler-runtime`, `react`, `../context/overlayContext`, `../keybindings/KeybindingContext`, `../keybindings/useKeybinding`, `../utils/handlePromptSubmit`

**Main flow:** Entry: `CommandKeybindingHandlers()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useCommandQueue.ts` (15 lines)

**Exports:**
- `useCommandQueue()`

**Dependencies:** `react`, `../types/textInputTypes`

**Main flow:** Entry: `useCommandQueue()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useCopyOnSelect.ts` (98 lines)

**Exports:**
- `useCopyOnSelect()`
- `useSelectionBgColor()`

**Dependencies:** `react`, `../components/design-system/ThemeProvider`, `../ink/hooks/use-selection`, `../utils/config`, `../utils/theme`

**Main flow:** Entry: `useCopyOnSelect()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useDeferredHookMessages.ts` (46 lines)

**Exports:**
- `useDeferredHookMessages()`

**Dependencies:** `react`, `../types/message`

**Main flow:** Entry: `useDeferredHookMessages()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useDiffData.ts` (110 lines)

**Exports:**
- `DiffFile`
- `DiffData`
- `useDiffData()`

**Dependencies:** `diff`, `react`

**Main flow:** Entry: `useDiffData()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useDiffInIDE.ts` (379 lines)

**Exports:**
- `useDiffInIDE()`
- `computeEditsFromContents()`

**Dependencies:** `crypto`, `path`, `react`, `src/services/analytics/index`, `src/utils/fileRead`, `src/utils/path`, `../components/permissions/FilePermissionDialog/permissionOptions`, `../Tool`, `../tools/FileEditTool/types`, `../utils/config`

**Main flow:** Entry: `useDiffInIDE()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useDirectConnect.ts` (229 lines)

**Exports:**
- `useDirectConnect()`

**Dependencies:** `react`, `../components/permissions/PermissionRequest`, `../remote/RemoteSessionManager`, `../Tool`, `../types/message`, `../types/permissions`, `../utils/debug`, `../utils/gracefulShutdown`, `../utils/teleport/api`

**Main flow:** Entry: `useDirectConnect()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useDoublePress.ts` (62 lines)

**Exports:**
- `DOUBLE_PRESS_TIMEOUT_MS`
- `useDoublePress()`

**Dependencies:** `react`

**Main flow:** Entry: `useDoublePress()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useDynamicConfig.ts` (22 lines)

**Exports:**
- `useDynamicConfig()`

**Dependencies:** `react`, `../services/analytics/growthbook`

**Main flow:** Entry: `useDynamicConfig()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useElapsedTime.ts` (37 lines)

**Exports:**
- `useElapsedTime()`

**Dependencies:** `react`, `../utils/format`

**Main flow:** Entry: `useElapsedTime()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useExitOnCtrlCD.ts` (95 lines)

**Exports:**
- `ExitState`
- `useExitOnCtrlCD()`

**Dependencies:** `react`, `../ink/hooks/use-app`, `../keybindings/types`, `./useDoublePress`

**Main flow:** Entry: `useExitOnCtrlCD()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useExitOnCtrlCDWithKeybindings.ts` (24 lines)

**Exports:**
- `useExitOnCtrlCDWithKeybindings()`

**Dependencies:** `../keybindings/useKeybinding`, `./useExitOnCtrlCD`

**Main flow:** Entry: `useExitOnCtrlCDWithKeybindings()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useFileHistorySnapshotInit.ts` (25 lines)

**Exports:**
- `useFileHistorySnapshotInit()`

**Dependencies:** `react`

**Main flow:** Entry: `useFileHistorySnapshotInit()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useGlobalKeybindings.tsx` (249 lines)

**Exports:**
- `GlobalKeybindingHandlers()`

**Dependencies:** `bun:bundle`, `react`, `../ink/instances`, `../keybindings/useKeybinding`, `../screens/REPL`, `../services/analytics/growthbook`, `../services/analytics/index`, `../state/AppState`, `../utils/array`, `../utils/terminalPanel`

**Feature gates:** `KAIROS`, `KAIROS_BRIEF`, `TERMINAL_PANEL`

**Main flow:** Entry: `GlobalKeybindingHandlers()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useHistorySearch.ts` (303 lines)

**Exports:**
- `useHistorySearch()`

**Dependencies:** `bun:bundle`, `react`, `../history`, `../ink/events/keyboard-event`, `../ink`, `../keybindings/useKeybinding`, `../types/textInputTypes`, `../utils/config`

**Feature gates:** `HISTORY_PICKER`

**Main flow:** Entry: `useHistorySearch()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useIDEIntegration.tsx` (70 lines)

**Exports:**
- `useIDEIntegration()`

**Dependencies:** `react/compiler-runtime`, `react`, `../services/mcp/types`, `../utils/config`, `../utils/envUtils`, `../utils/ide`

**Main flow:** Entry: `useIDEIntegration()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useIdeAtMentioned.ts` (76 lines)

**Exports:**
- `IDEAtMentioned`
- `useIdeAtMentioned()`

**Dependencies:** `react`, `src/utils/log`, `zod/v4`, `../utils/ide`, `../utils/lazySchema`

**Main flow:** Entry: `useIdeAtMentioned()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useIdeConnectionStatus.ts` (33 lines)

**Exports:**
- `IdeStatus`
- `useIdeConnectionStatus()`

**Dependencies:** `react`, `../services/mcp/types`

**Main flow:** Entry: `useIdeConnectionStatus()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useIdeLogging.ts` (41 lines)

**Exports:**
- `useIdeLogging()`

**Dependencies:** `react`, `src/services/analytics/index`, `zod/v4`, `../services/mcp/types`, `../utils/ide`, `../utils/lazySchema`

**Main flow:** Entry: `useIdeLogging()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useIdeSelection.ts` (150 lines)

**Exports:**
- `SelectionPoint`
- `SelectionData`
- `IDESelection`
- `useIdeSelection()`

**Dependencies:** `react`, `src/utils/log`, `zod/v4`, `../utils/ide`, `../utils/lazySchema`

**Main flow:** Entry: `useIdeSelection()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useInboxPoller.ts` (969 lines)

**Exports:**
- `useInboxPoller()`

**Dependencies:** `crypto`, `react`, `usehooks-ts`, `../components/permissions/PermissionRequest`, `../constants/xml`, `../ink/useTerminalNotification`, `../services/notifier`, `../Tool`, `../tasks/InProcessTeammateTask/types`, `../tools`

**Main flow:** Entry: `useInboxPoller()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useInputBuffer.ts` (132 lines)

**Exports:**
- `BufferEntry`
- `UseInputBufferProps`
- `UseInputBufferResult`
- `useInputBuffer()`

**Dependencies:** `react`, `../utils/config`

**Main flow:** Entry: `useInputBuffer()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useIssueFlagBanner.ts` (133 lines)

**Exports:**
- `isSessionContainerCompatible()`
- `hasFrictionSignal()`
- `useIssueFlagBanner()`

**Dependencies:** `react`, `../tools/BashTool/toolName`, `../types/message`, `../utils/messages`

**Main flow:** Entry: `isSessionContainerCompatible()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useLogMessages.ts` (119 lines)

**Exports:**
- `useLogMessages()`

**Dependencies:** `crypto`, `react`, `../state/AppState`, `../types/message`, `../utils/agentSwarmsEnabled`

**Main flow:** Entry: `useLogMessages()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useLspPluginRecommendation.tsx` (194 lines)

**Exports:**
- `LspRecommendationState`
- `useLspPluginRecommendation()`

**Dependencies:** `react/compiler-runtime`, `path`, `react`, `../bootstrap/state`, `../context/notifications`, `../state/AppState`, `../utils/config`, `../utils/debug`, `../utils/log`, `../utils/plugins/lspRecommendation`

**Main flow:** Entry: `useLspPluginRecommendation()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useMailboxBridge.ts` (21 lines)

**Exports:**
- `useMailboxBridge()`

**Dependencies:** `react`, `../context/mailbox`

**Main flow:** Entry: `useMailboxBridge()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useMainLoopModel.ts` (34 lines)

**Exports:**
- `useMainLoopModel()`

**Dependencies:** `react`, `../services/analytics/growthbook`, `../state/AppState`

**Main flow:** Entry: `useMainLoopModel()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useManagePlugins.ts` (304 lines)

**Exports:**
- `useManagePlugins()`

**Dependencies:** `react`, `../commands`, `../context/notifications`, `../services/lsp/manager`, `../state/AppState`, `../tools/AgentTool/loadAgentsDir`, `../utils/array`, `../utils/debug`, `../utils/diagLogs`, `../utils/errors`

**Main flow:** Entry: `useManagePlugins()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useMemoryUsage.ts` (39 lines)

**Exports:**
- `MemoryUsageStatus`
- `MemoryUsageInfo`
- `useMemoryUsage()`

**Dependencies:** `react`, `usehooks-ts`

**Main flow:** Entry: `useMemoryUsage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useMergedClients.ts` (23 lines)

**Exports:**
- `mergeClients()`
- `useMergedClients()`

**Dependencies:** `lodash-es/uniqBy`, `react`, `../services/mcp/types`

**Main flow:** Entry: `mergeClients()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useMergedCommands.ts` (15 lines)

**Exports:**
- `useMergedCommands()`

**Dependencies:** `lodash-es/uniqBy`, `react`, `../commands`

**Main flow:** Entry: `useMergedCommands()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useMergedTools.ts` (44 lines)

**Exports:**
- `useMergedTools()`

**Dependencies:** `react`, `../Tool`, `../tools`, `../state/AppState`, `../utils/toolPool`

**Main flow:** Entry: `useMergedTools()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useMinDisplayTime.ts` (35 lines)

**Exports:**
- `useMinDisplayTime()`

**Dependencies:** `react`

**Main flow:** Entry: `useMinDisplayTime()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useNotifyAfterTimeout.ts` (65 lines)

**Exports:**
- `DEFAULT_INTERACTION_THRESHOLD_MS`
- `useNotifyAfterTimeout()`

**Dependencies:** `react`, `../ink/useTerminalNotification`, `../services/notifier`

**Main flow:** Entry: `useNotifyAfterTimeout()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useOfficialMarketplaceNotification.tsx` (48 lines)

**Exports:**
- `useOfficialMarketplaceNotification()`

**Dependencies:** `react`, `../context/notifications`, `../ink`, `../utils/debug`, `../utils/plugins/officialMarketplaceStartupCheck`, `./notifs/useStartupNotification`

**Main flow:** Entry: `useOfficialMarketplaceNotification()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/usePasteHandler.ts` (285 lines)

**Exports:**
- `usePasteHandler()`

**Dependencies:** `path`, `react`, `src/utils/log`, `usehooks-ts`, `../ink`, `../utils/imageResizer`, `../utils/platform`

**Main flow:** Entry: `usePasteHandler()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/usePluginRecommendationBase.tsx` (105 lines)

**Exports:**
- `usePluginRecommendationBase()`
- `installPluginAndNotify()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../bootstrap/state`, `../context/notifications`, `../ink`, `../utils/log`, `../utils/plugins/marketplaceManager`

**Main flow:** Entry: `usePluginRecommendationBase()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/usePrStatus.ts` (106 lines)

**Exports:**
- `PrStatusState`
- `usePrStatus()`

**Dependencies:** `react`, `../bootstrap/state`, `../utils/ghPrStatus`

**Main flow:** Entry: `usePrStatus()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/usePromptSuggestion.ts` (177 lines)

**Exports:**
- `usePromptSuggestion()`

**Dependencies:** `react`, `../ink/hooks/use-terminal-focus`, `../services/PromptSuggestion/speculation`, `../state/AppState`

**Main flow:** Entry: `usePromptSuggestion()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/usePromptsFromClaudeInChrome.tsx` (71 lines)

**Exports:**
- `usePromptsFromClaudeInChrome()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/messages.mjs`, `react`, `src/utils/log`, `zod/v4`, `../services/mcp/client`, `../services/mcp/types`, `../types/permissions`, `../utils/claudeInChrome/common`, `../utils/lazySchema`

**Main flow:** Entry: `usePromptsFromClaudeInChrome()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useQueueProcessor.ts` (68 lines)

**Exports:**
- `useQueueProcessor()`

**Dependencies:** `react`, `../types/textInputTypes`, `../utils/QueryGuard`, `../utils/queueProcessor`

**Main flow:** Entry: `useQueueProcessor()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useRemoteSession.ts` (605 lines)

**Exports:**
- `useRemoteSession()`

**Dependencies:** `react`, `../bridge/bridgeMessaging`, `../components/permissions/PermissionRequest`, `../components/Spinner/types`, `../state/AppState`, `../state/AppStateStore`, `../Tool`, `../types/message`, `../types/permissions`

**Main flow:** Entry: `useRemoteSession()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useReplBridge.tsx` (723 lines)

**Exports:**
- `BRIDGE_FAILURE_DISMISS_MS`
- `useReplBridge()`

**Dependencies:** `bun:bundle`, `react`, `../bootstrap/state`, `../bridge/bridgePermissionCallbacks`, `../bridge/bridgeStatusUtil`, `../bridge/inboundMessages`, `../bridge/replBridge`, `../bridge/replBridgeHandle`, `../commands`

**Feature gates:** `BRIDGE_MODE`, `KAIROS`, `KAIROS_GITHUB_WEBHOOKS`, `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `useReplBridge()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useSSHSession.ts` (241 lines)

**Exports:**
- `useSSHSession()`

**Dependencies:** `crypto`, `react`, `../components/permissions/PermissionRequest`, `../ssh/createSSHSession`, `../ssh/SSHSessionManager`, `../Tool`, `../types/message`, `../types/permissions`, `../utils/debug`

**Main flow:** Entry: `useSSHSession()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useScheduledTasks.ts` (139 lines)

**Exports:**
- `useScheduledTasks()`

**Dependencies:** `react`, `../state/AppState`, `../Task`, `../tools/ScheduleCronTool/prompt`, `../types/message`, `../utils/cronJitterConfig`, `../utils/cronScheduler`, `../utils/cronTasks`, `../utils/debug`, `../utils/messageQueueManager`

**Main flow:** Entry: `useScheduledTasks()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useSearchInput.ts` (364 lines)

**Exports:**
- `useSearchInput()`

**Dependencies:** `react`, `../ink/events/keyboard-event`, `../ink`, `./useTerminalSize`

**Main flow:** Entry: `useSearchInput()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useSessionBackgrounding.ts` (158 lines)

**Exports:**
- `useSessionBackgrounding()`

**Dependencies:** `react`, `../state/AppState`, `../types/message`

**Main flow:** Entry: `useSessionBackgrounding()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useSettings.ts` (17 lines)

**Exports:**
- `ReadonlySettings`
- `useSettings()`

**Dependencies:** `../state/AppState`

**Main flow:** Entry: `useSettings()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useSettingsChange.ts` (25 lines)

**Exports:**
- `useSettingsChange()`

**Dependencies:** `react`, `../utils/settings/changeDetector`, `../utils/settings/constants`, `../utils/settings/settings`, `../utils/settings/types`

**Main flow:** Entry: `useSettingsChange()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useSkillImprovementSurvey.ts` (105 lines)

**Exports:**
- `useSkillImprovementSurvey()`

**Dependencies:** `react`, `../components/FeedbackSurvey/utils`, `../state/AppState`, `../types/message`, `../utils/hooks/skillImprovement`, `../utils/messages`

**Main flow:** Entry: `useSkillImprovementSurvey()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useSkillsChange.ts` (62 lines)

**Exports:**
- `useSkillsChange()`

**Dependencies:** `react`, `../commands`, `../services/analytics/growthbook`, `../utils/log`, `../utils/skills/skillChangeDetector`

**Main flow:** Entry: `useSkillsChange()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useSwarmInitialization.ts` (81 lines)

**Exports:**
- `useSwarmInitialization()`

**Dependencies:** `react`, `../bootstrap/state`, `../state/AppState`, `../types/message`, `../utils/agentSwarmsEnabled`, `../utils/swarm/reconnection`, `../utils/swarm/teamHelpers`, `../utils/swarm/teammateInit`, `../utils/teammate`

**Main flow:** Entry: `useSwarmInitialization()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useSwarmPermissionPoller.ts` (330 lines)

**Exports:**
- `PermissionResponseCallback`
- `registerPermissionCallback()`
- `unregisterPermissionCallback()`
- `hasPermissionCallback()`
- `clearAllPendingCallbacks()`
- `processMailboxPermissionResponse()`
- `SandboxPermissionResponseCallback`
- `registerSandboxPermissionCallback()`
- `hasSandboxPermissionCallback()`
- `processSandboxPermissionResponse()`
- `useSwarmPermissionPoller()`

**Dependencies:** `react`, `usehooks-ts`, `../utils/debug`, `../utils/errors`, `../utils/teammate`

**Main flow:** Entry: `registerPermissionCallback()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useTaskListWatcher.ts` (221 lines)

**Exports:**
- `useTaskListWatcher()`

**Dependencies:** `fs`, `react`, `../utils/debug`

**Main flow:** Entry: `useTaskListWatcher()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useTasksV2.ts` (250 lines)

**Exports:**
- `useTasksV2()`
- `useTasksV2WithCollapseEffect()`

**Dependencies:** `fs`, `react`, `../state/AppState`, `../utils/signal`, `../utils/tasks`, `../utils/teammate`

**Main flow:** Entry: `useTasksV2()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useTeammateViewAutoExit.ts` (63 lines)

**Exports:**
- `useTeammateViewAutoExit()`

**Dependencies:** `react`, `../state/AppState`, `../state/teammateViewHelpers`, `../tasks/InProcessTeammateTask/types`

**Main flow:** Entry: `useTeammateViewAutoExit()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useTeleportResume.tsx` (85 lines)

**Exports:**
- `TeleportResumeError`
- `TeleportSource`
- `useTeleportResume()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/bootstrap/state`, `src/services/analytics/index`, `src/utils/conversationRecovery`, `src/utils/teleport/api`, `../utils/errors`, `../utils/teleport`

**Main flow:** Entry: `useTeleportResume()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useTerminalSize.ts` (15 lines)

**Exports:**
- `useTerminalSize()`

**Dependencies:** `react`

**Main flow:** Entry: `useTerminalSize()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useTextInput.ts` (529 lines)

**Exports:**
- `UseTextInputProps`
- `useTextInput()`

**Dependencies:** `src/components/PromptInput/inputModes`, `src/context/notifications`, `strip-ansi`, `../commands/terminalSetup/terminalSetup`, `../history`, `../ink`, `../utils/env`, `../utils/fullscreen`, `../utils/imageResizer`, `../utils/modifiers`

**Main flow:** Entry: `useTextInput()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useTimeout.ts` (14 lines)

**Exports:**
- `useTimeout()`

**Dependencies:** `react`

**Main flow:** Entry: `useTimeout()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useTurnDiffs.ts` (213 lines)

**Exports:**
- `TurnFileDiff`
- `TurnDiff`
- `useTurnDiffs()`

**Dependencies:** `diff`, `react`, `../tools/FileEditTool/types`, `../tools/FileWriteTool/FileWriteTool`, `../types/message`

**Main flow:** Entry: `useTurnDiffs()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useTypeahead.tsx` (1385 lines)

**Exports:**
- `extractSearchToken()`
- `formatReplacementValue()`
- `applyShellSuggestion()`
- `applyDirectorySuggestion()`
- `extractCompletionToken()`
- `useTypeahead()`

**Dependencies:** `react`, `src/context/notifications`, `src/ink`, `src/services/analytics/index`, `usehooks-ts`, `../commands`, `../components/PromptInput/inputModes`, `../components/PromptInput/PromptInputFooterSuggestions`, `../context/overlayContext`

**Main flow:** Entry: `extractSearchToken()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useUpdateNotification.ts` (34 lines)

**Exports:**
- `getSemverPart()`
- `shouldShowUpdateNotification()`
- `useUpdateNotification()`

**Dependencies:** `react`, `semver`

**Main flow:** Entry: `getSemverPart()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useVimInput.ts` (316 lines)

**Exports:**
- `useVimInput()`

**Dependencies:** `react`, `../ink`, `../types/textInputTypes`, `../utils/Cursor`, `../utils/intl`, `../vim/transitions`, `./useTextInput`

**Main flow:** Entry: `useVimInput()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useVirtualScroll.ts` (721 lines)

**Exports:**
- `VirtualScrollResult`
- `useVirtualScroll()`

**Dependencies:** `react`, `../ink/components/ScrollBox`, `../ink/dom`

**Main flow:** Entry: `useVirtualScroll()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useVoice.ts` (1144 lines)

**Exports:**
- `normalizeLanguageForSTT()`
- `FIRST_PRESS_FALLBACK_MS`
- `computeLevel()`
- `useVoice()`

**Dependencies:** `react`, `../context/voice`, `../ink/hooks/use-terminal-focus`, `../services/voiceKeyterms`, `../utils/debug`, `../utils/errors`, `../utils/intl`, `../utils/log`, `../utils/settings/settings`, `../utils/sleep`

**Main flow:** Entry: `normalizeLanguageForSTT()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useVoiceEnabled.ts` (25 lines)

**Exports:**
- `useVoiceEnabled()`

**Dependencies:** `react`, `../state/AppState`

**Main flow:** Entry: `useVoiceEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `hooks/useVoiceIntegration.tsx` (677 lines)

**Exports:**
- `useVoiceIntegration()`
- `useVoiceKeybindingHandler()`
- `VoiceKeybindingHandler()`

**Dependencies:** `bun:bundle`, `react`, `../context/notifications`, `../context/overlayContext`, `../context/voice`, `../ink/events/keyboard-event`, `../ink`, `../keybindings/KeybindingContext`, `../keybindings/resolver`

**Feature gates:** `VOICE_MODE`

**Main flow:** Entry: `useVoiceIntegration()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/Ansi.tsx` (292 lines)

**Exports:**
- `Ansi`

**Dependencies:** `react/compiler-runtime`, `react`, `./components/Link`, `./components/Text`, `./styles`, `./termio`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/bidi.ts` (139 lines)

**Exports:**
- `reorderBidi()`

**Dependencies:** `bidi-js`

**Main flow:** Entry: `reorderBidi()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/clearTerminal.ts` (74 lines)

**Exports:**
- `getClearTerminalSequence()`
- `clearTerminal`

**Dependencies:** local only

**Main flow:** Entry: `getClearTerminalSequence()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/colorize.ts` (231 lines)

**Exports:**
- `CHALK_BOOSTED_FOR_XTERMJS`
- `CHALK_CLAMPED_FOR_TMUX`
- `ColorType`
- `colorize`
- `applyTextStyles()`
- `applyColor()`

**Dependencies:** `chalk`, `./styles`

**Main flow:** Entry: `applyTextStyles()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/components/AlternateScreen.tsx` (80 lines)

**Exports:**
- `AlternateScreen()`

**Dependencies:** `react/compiler-runtime`, `react`, `../instances`, `../termio/dec`, `../useTerminalNotification`, `./Box`, `./TerminalSizeContext`

**Main flow:** Entry: `AlternateScreen()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/components/App.tsx` (658 lines)

**Exports:**
- `handleMouseEvent()`

**Dependencies:** `react`, `../../bootstrap/state`, `../../utils/debug`, `../../utils/earlyInput`, `../../utils/envUtils`, `../../utils/fullscreen`, `../../utils/log`, `../events/emitter`, `../events/input-event`, `../events/terminal-focus-event`

**Main flow:** Entry: `handleMouseEvent()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/components/AppContext.ts` (21 lines)

**Exports:**
- `Props`

**Dependencies:** `react`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/components/Box.tsx` (214 lines)

**Exports:**
- `Props`

**Dependencies:** `react/compiler-runtime`, `react`, `type-fest`, `../dom`, `../events/click-event`, `../events/focus-event`, `../events/keyboard-event`, `../styles`, `../warn`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/components/Button.tsx` (192 lines)

**Exports:**
- `Props`

**Dependencies:** `react/compiler-runtime`, `react`, `type-fest`, `../dom`, `../events/click-event`, `../events/focus-event`, `../events/keyboard-event`, `../styles`, `./Box`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/components/ClockContext.tsx` (112 lines)

**Exports:**
- `Clock`
- `createClock()`
- `ClockContext`
- `ClockProvider()`

**Dependencies:** `react/compiler-runtime`, `react`, `../constants`, `../hooks/use-terminal-focus`

**Main flow:** Entry: `createClock()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/components/CursorDeclarationContext.ts` (32 lines)

**Exports:**
- `CursorDeclaration`
- `CursorDeclarationSetter`

**Dependencies:** `react`, `../dom`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/components/ErrorOverview.tsx` (109 lines)

**Exports:**
- default `ErrorOverview()`

**Dependencies:** `code-excerpt`, `fs`, `react`, `stack-utils`, `./Box`, `./Text`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/components/Link.tsx` (42 lines)

**Exports:**
- `Props`
- default `Link()`

**Dependencies:** `react/compiler-runtime`, `react`, `../supports-hyperlinks`, `./Text`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/components/Newline.tsx` (39 lines)

**Exports:**
- `Props`
- default `Newline()`

**Dependencies:** `react/compiler-runtime`, `react`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/components/NoSelect.tsx` (68 lines)

**Exports:**
- `NoSelect()`

**Dependencies:** `react/compiler-runtime`, `react`, `./Box`

**Main flow:** Entry: `NoSelect()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/components/RawAnsi.tsx` (57 lines)

**Exports:**
- `RawAnsi()`

**Dependencies:** `react/compiler-runtime`, `react`

**Main flow:** Entry: `RawAnsi()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/components/ScrollBox.tsx` (237 lines)

**Exports:**
- `ScrollBoxHandle`
- `ScrollBoxProps`

**Dependencies:** `react`, `type-fest`, `../../bootstrap/state`, `../dom`, `../reconciler`, `../styles`, `./Box`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/components/Spacer.tsx` (20 lines)

**Exports:**
- default `Spacer()`

**Dependencies:** `react/compiler-runtime`, `react`, `./Box`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/components/StdinContext.ts` (49 lines)

**Exports:**
- `Props`

**Dependencies:** `react`, `../events/emitter`, `../terminal-querier`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/components/TerminalFocusContext.tsx` (52 lines)

**Exports:**
- `TerminalFocusContextProps`
- `TerminalFocusProvider()`

**Dependencies:** `react/compiler-runtime`, `react`, `../terminal-focus-state`

**Main flow:** Entry: `TerminalFocusProvider()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/components/TerminalSizeContext.tsx` (7 lines)

**Exports:**
- `TerminalSize`
- `TerminalSizeContext`

**Dependencies:** `react`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/components/Text.tsx` (254 lines)

**Exports:**
- `Props`
- default `Text()`

**Dependencies:** `react/compiler-runtime`, `react`, `../styles`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/constants.ts` (2 lines)

**Exports:**
- `FRAME_INTERVAL_MS`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/dom.ts` (484 lines)

**Exports:**
- `TextName`
- `ElementNames`
- `NodeNames`
- `DOMElement`
- `TextNode`
- `DOMNode`
- `DOMNodeAttribute`
- `createNode`
- `appendChildNode`
- `insertBeforeNode`
- `removeChildNode`
- `setAttribute`
- `setStyle`
- `setTextStyles`
- `createTextNode`
- `markDirty`
- `scheduleRenderFrom`
- `setTextNodeValue`
- `clearYogaNodeReferences`
- `findOwnerChainAtRow()`

**Dependencies:** `./focus`, `./layout/engine`, `./layout/node`, `./measure-text`, `./node-cache`, `./squash-text-nodes`, `./styles`, `./tabstops`, `./wrap-text`

**Main flow:** Entry: `findOwnerChainAtRow()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/events/click-event.ts` (38 lines)

**Exports:**
- `ClickEvent`

**Dependencies:** `./event`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/events/dispatcher.ts` (233 lines)

**Exports:**
- `Dispatcher`

**Dependencies:** `../../utils/log`, `./event-handlers`, `./terminal-event`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/events/emitter.ts` (39 lines)

**Exports:**
- `EventEmitter`

**Dependencies:** `events`, `./event`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/events/event-handlers.ts` (73 lines)

**Exports:**
- `EventHandlerProps`
- `HANDLER_FOR_EVENT`
- `EVENT_HANDLER_PROPS`

**Dependencies:** `./click-event`, `./focus-event`, `./keyboard-event`, `./paste-event`, `./resize-event`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/events/event.ts` (11 lines)

**Exports:**
- `Event`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/events/focus-event.ts` (21 lines)

**Exports:**
- `FocusEvent`

**Dependencies:** `./terminal-event`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/events/input-event.ts` (205 lines)

**Exports:**
- `Key`
- `InputEvent`

**Dependencies:** `../parse-keypress`, `./event`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/events/keyboard-event.ts` (51 lines)

**Exports:**
- `KeyboardEvent`

**Dependencies:** `../parse-keypress`, `./terminal-event`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/events/terminal-event.ts` (107 lines)

**Exports:**
- `TerminalEvent`
- `EventTarget`

**Dependencies:** `./event`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/events/terminal-focus-event.ts` (19 lines)

**Exports:**
- `TerminalFocusEventType`
- `TerminalFocusEvent`

**Dependencies:** `./event`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/focus.ts` (181 lines)

**Exports:**
- `FocusManager`
- `getRootNode()`
- `getFocusManager()`

**Dependencies:** `./dom`, `./events/focus-event`

**Main flow:** Entry: `getRootNode()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/frame.ts` (124 lines)

**Exports:**
- `Frame`
- `emptyFrame()`
- `FlickerReason`
- `FrameEvent`
- `Patch`
- `Diff`
- `shouldClearScreen()`

**Dependencies:** `./cursor`, `./layout/geometry`, `./render-node-to-output`

**Main flow:** Entry: `emptyFrame()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/get-max-width.ts` (27 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `./layout/node`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/hit-test.ts` (130 lines)

**Exports:**
- `hitTest()`
- `dispatchClick()`
- `dispatchHover()`

**Dependencies:** `./dom`, `./events/click-event`, `./events/event-handlers`, `./node-cache`

**Main flow:** Entry: `hitTest()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/hooks/use-animation-frame.ts` (57 lines)

**Exports:**
- `useAnimationFrame()`

**Dependencies:** `react`, `../components/ClockContext`, `../dom`, `./use-terminal-viewport`

**Main flow:** Entry: `useAnimationFrame()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/hooks/use-app.ts` (8 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `react`, `../components/AppContext`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/hooks/use-declared-cursor.ts` (73 lines)

**Exports:**
- `useDeclaredCursor()`

**Dependencies:** `react`, `../components/CursorDeclarationContext`, `../dom`

**Main flow:** Entry: `useDeclaredCursor()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/hooks/use-input.ts` (92 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `react`, `usehooks-ts`, `../events/input-event`, `./use-stdin`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/hooks/use-interval.ts` (67 lines)

**Exports:**
- `useAnimationTimer()`
- `useInterval()`

**Dependencies:** `react`, `../components/ClockContext`

**Main flow:** Entry: `useAnimationTimer()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/hooks/use-search-highlight.ts` (53 lines)

**Exports:**
- `useSearchHighlight()`

**Dependencies:** `react`, `../components/StdinContext`, `../dom`, `../instances`, `../render-to-screen`

**Main flow:** Entry: `useSearchHighlight()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/hooks/use-selection.ts` (104 lines)

**Exports:**
- `useSelection()`
- `useHasSelection()`

**Dependencies:** `react`, `../components/StdinContext`, `../instances`

**Main flow:** Entry: `useSelection()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/hooks/use-stdin.ts` (8 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `react`, `../components/StdinContext`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/hooks/use-tab-status.ts` (72 lines)

**Exports:**
- `TabStatusKind`
- `useTabStatus()`

**Dependencies:** `react`, `../termio/types`, `../useTerminalNotification`

**Main flow:** Entry: `useTabStatus()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/hooks/use-terminal-focus.ts` (16 lines)

**Exports:**
- `useTerminalFocus()`

**Dependencies:** `react`, `../components/TerminalFocusContext`

**Main flow:** Entry: `useTerminalFocus()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/hooks/use-terminal-title.ts` (31 lines)

**Exports:**
- `useTerminalTitle()`

**Dependencies:** `react`, `strip-ansi`, `../termio/osc`, `../useTerminalNotification`

**Main flow:** Entry: `useTerminalTitle()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/hooks/use-terminal-viewport.ts` (96 lines)

**Exports:**
- `useTerminalViewport()`

**Dependencies:** `react`, `../components/TerminalSizeContext`, `../dom`

**Main flow:** Entry: `useTerminalViewport()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/ink.tsx` (1723 lines)

**Exports:**
- `Options`
- `drainStdin()`

**Dependencies:** `auto-bind`, `fs`, `lodash-es/noop`, `lodash-es/throttle`, `react`, `react-reconciler`, `react-reconciler/constants`, `signal-exit`, `src/bootstrap/state`, `src/native-ts/yoga-layout/index`

**Main flow:** Entry: `drainStdin()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/instances.ts` (10 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `./ink`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/layout/engine.ts` (6 lines)

**Exports:**
- `createLayoutNode()`

**Dependencies:** `./node`, `./yoga`

**Main flow:** Entry: `createLayoutNode()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/layout/geometry.ts` (97 lines)

**Exports:**
- `Point`
- `Size`
- `Rectangle`
- `Edges`
- `edges()`
- `edges()`
- `edges()`
- `edges()`
- `addEdges()`
- `ZERO_EDGES`
- `resolveEdges()`
- `unionRect()`
- `clampRect()`
- `withinBounds()`
- `clamp()`

**Dependencies:** local only

**Main flow:** Entry: `edges()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/layout/node.ts` (152 lines)

**Exports:**
- `LayoutEdge`
- `LayoutEdge`
- `LayoutGutter`
- `LayoutGutter`
- `LayoutDisplay`
- `LayoutDisplay`
- `LayoutFlexDirection`
- `LayoutFlexDirection`
- `LayoutAlign`
- `LayoutAlign`
- `LayoutJustify`
- `LayoutJustify`
- `LayoutWrap`
- `LayoutWrap`
- `LayoutPositionType`
- `LayoutPositionType`
- `LayoutOverflow`
- `LayoutOverflow`
- `LayoutMeasureFunc`
- `LayoutMeasureMode`
- `LayoutMeasureMode`
- `LayoutNode`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/layout/yoga.ts` (308 lines)

**Exports:**
- `YogaLayoutNode`
- `createYogaLayoutNode()`

**Dependencies:** local only

**Main flow:** Entry: `createYogaLayoutNode()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/line-width-cache.ts` (24 lines)

**Exports:**
- `lineWidth()`

**Dependencies:** `./stringWidth`

**Main flow:** Entry: `lineWidth()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/log-update.ts` (773 lines)

**Exports:**
- `LogUpdate`

**Dependencies:** `../utils/debug`, `./frame`, `./layout/geometry`, `./termio/osc`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/measure-element.ts` (23 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `./dom`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/measure-text.ts` (47 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `./line-width-cache`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/node-cache.ts` (54 lines)

**Exports:**
- `CachedLayout`
- `nodeCache`
- `pendingClears`
- `addPendingClear()`
- `consumeAbsoluteRemovedFlag()`

**Dependencies:** `./dom`, `./layout/geometry`

**Main flow:** Entry: `addPendingClear()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/optimizer.ts` (93 lines)

**Exports:**
- `optimize()`

**Dependencies:** `./frame`

**Main flow:** Entry: `optimize()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/output.ts` (797 lines)

**Exports:**
- `Operation`
- `Clip`

**Dependencies:** `../utils/debug`, `../utils/intl`, `../utils/sliceAnsi`, `./bidi`, `./layout/geometry`, `./stringWidth`, `./widest-line`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/parse-keypress.ts` (801 lines)

**Exports:**
- `DECRPM_STATUS`
- `TerminalResponse`
- `KeyParseState`
- `INITIAL_STATE`
- `parseMultipleKeypresses()`
- `nonAlphanumericKeys`
- `ParsedKey`
- `ParsedResponse`
- `ParsedMouse`
- `ParsedInput`

**Dependencies:** `buffer`, `./termio/csi`, `./termio/tokenize`

**Main flow:** Entry: `parseMultipleKeypresses()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/reconciler.ts` (512 lines)

**Exports:**
- `getOwnerChain()`
- `isDebugRepaintsEnabled()`
- `dispatcher`
- `recordYogaMs()`
- `getLastYogaMs()`
- `markCommitStart()`
- `getLastCommitMs()`
- `resetProfileCounters()`

**Dependencies:** `fs`, `react-reconciler`, `src/native-ts/yoga-layout/index`, `../utils/envUtils`, `./events/dispatcher`, `./events/event-handlers`, `./focus`, `./layout/node`, `./styles`

**Main flow:** Entry: `getOwnerChain()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/render-border.ts` (231 lines)

**Exports:**
- `BorderTextOptions`
- `CUSTOM_BORDER_STYLES`
- `BorderStyle`

**Dependencies:** `chalk`, `cli-boxes`, `./colorize`, `./dom`, `./output`, `./stringWidth`, `./styles`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/render-node-to-output.ts` (1462 lines)

**Exports:**
- `resetLayoutShifted()`
- `didLayoutShift()`
- `ScrollHint`
- `resetScrollHint()`
- `getScrollHint()`
- `resetScrollDrainNode()`
- `getScrollDrainNode()`
- `FollowScroll`
- `consumeFollowScroll()`

**Dependencies:** `indent-string`, `./colorize`, `./dom`, `./get-max-width`, `./layout/geometry`, `./layout/node`, `./node-cache`, `./output`, `./render-border`, `./screen`

**Main flow:** Entry: `resetLayoutShifted()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/render-to-screen.ts` (231 lines)

**Exports:**
- `MatchPosition`
- `renderToScreen()`
- `scanPositions()`
- `applyPositionedHighlight()`

**Dependencies:** `lodash-es/noop`, `react`, `react-reconciler/constants`, `../utils/debug`, `./dom`, `./focus`, `./output`, `./reconciler`

**Main flow:** Entry: `renderToScreen()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/renderer.ts` (178 lines)

**Exports:**
- `RenderOptions`
- `Renderer`
- default `createRenderer()`

**Dependencies:** `src/utils/debug`, `./dom`, `./frame`, `./node-cache`, `./output`, `./screen`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/root.ts` (184 lines)

**Exports:**
- `RenderOptions`
- `Instance`
- `Root`
- `renderSync`
- `createRoot()`

**Dependencies:** `react`, `src/utils/debug`, `stream`, `./frame`, `./ink`, `./instances`

**Main flow:** Entry: `createRoot()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/screen.ts` (1486 lines)

**Exports:**
- `CharPool`
- `HyperlinkPool`
- `StylePool`
- `enum`
- `Hyperlink`
- `Cell`
- `Screen`
- `isEmptyCellAt()`
- `isCellEmpty()`
- `createScreen()`
- `resetScreen()`
- `migrateScreenPools()`
- `cellAt()`
- `cellAtIndex()`
- `visibleCellAtIndex()`
- `charInCellAt()`
- `setCellAt()`
- `setCellStyleId()`
- `blitRegion()`
- `clearRegion()`
- `shiftRows()`
- `OSC8_PREFIX`
- `extractHyperlinkFromStyles()`
- `filterOutHyperlinkStyles()`
- `diff()`
- ... +2 more

**Dependencies:** `./termio/ansi`, `./warn`

**Main flow:** Entry: `isEmptyCellAt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/searchHighlight.ts` (93 lines)

**Exports:**
- `applySearchHighlight()`

**Dependencies:** local only

**Main flow:** Entry: `applySearchHighlight()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/selection.ts` (917 lines)

**Exports:**
- `SelectionState`
- `createSelectionState()`
- `startSelection()`
- `updateSelection()`
- `finishSelection()`
- `clearSelection()`
- `selectWordAt()`
- `findPlainTextUrlAt()`
- `selectLineAt()`
- `extendSelection()`
- `FocusMove`
- `moveFocus()`
- `shiftSelection()`
- `shiftAnchor()`
- `shiftSelectionForFollow()`
- `hasSelection()`
- `selectionBounds()`
- `isCellSelected()`
- `getSelectedText()`
- `captureScrolledRows()`
- `applySelectionOverlay()`

**Dependencies:** `./layout/geometry`, `./screen`

**Main flow:** Entry: `createSelectionState()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/squash-text-nodes.ts` (92 lines)

**Exports:**
- `StyledSegment`
- `squashTextNodesToSegments()`

**Dependencies:** `./dom`, `./styles`

**Main flow:** Entry: `squashTextNodesToSegments()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/stringWidth.ts` (222 lines)

**Exports:**
- `stringWidth`

**Dependencies:** `emoji-regex`, `get-east-asian-width`, `strip-ansi`, `../utils/intl`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/styles.ts` (771 lines)

**Exports:**
- `RGBColor`
- `HexColor`
- `Ansi256Color`
- `AnsiColor`
- `Color`
- `TextStyles`
- `Styles`

**Dependencies:** `./render-border`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/supports-hyperlinks.ts` (57 lines)

**Exports:**
- `ADDITIONAL_HYPERLINK_TERMINALS`
- `supportsHyperlinks()`

**Dependencies:** `supports-hyperlinks`

**Main flow:** Entry: `supportsHyperlinks()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/tabstops.ts` (46 lines)

**Exports:**
- `expandTabs()`

**Dependencies:** `./stringWidth`, `./termio/tokenize`

**Main flow:** Entry: `expandTabs()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/terminal-focus-state.ts` (47 lines)

**Exports:**
- `TerminalFocusState`
- `setTerminalFocused()`
- `getTerminalFocused()`
- `getTerminalFocusState()`
- `subscribeTerminalFocus()`
- `resetTerminalFocusState()`

**Dependencies:** local only

**Main flow:** Entry: `setTerminalFocused()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/terminal-querier.ts` (212 lines)

**Exports:**
- `TerminalQuery`
- `decrqm()`
- `da1()`
- `da2()`
- `kittyKeyboard()`
- `cursorPosition()`
- `oscColor()`
- `xtversion()`
- `TerminalQuerier`

**Dependencies:** `./parse-keypress`, `./termio/csi`, `./termio/osc`

**Main flow:** Entry: `decrqm()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/terminal.ts` (248 lines)

**Exports:**
- `Progress`
- `isProgressReportingAvailable()`
- `isSynchronizedOutputSupported()`
- `setXtversionName()`
- `isXtermJs()`
- `supportsExtendedKeys()`
- `hasCursorUpViewportYankBug()`
- `SYNC_OUTPUT_SUPPORTED`
- `Terminal`
- `writeDiffToTerminal()`

**Dependencies:** `semver`, `stream`, `../utils/env`, `../utils/semver`, `./clearTerminal`, `./frame`, `./termio/csi`, `./termio/dec`, `./termio/osc`

**Main flow:** Entry: `isProgressReportingAvailable()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/termio.ts` (42 lines)

**Exports:**
- (none — internal module)

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/termio/ansi.ts` (75 lines)

**Exports:**
- `C0`
- `ESC`
- `BEL`
- `SEP`
- `ESC_TYPE`
- `isC0()`
- `isEscFinal()`

**Dependencies:** local only

**Main flow:** Entry: `isC0()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/termio/csi.ts` (319 lines)

**Exports:**
- `CSI_PREFIX`
- `CSI_RANGE`
- `isCSIParam()`
- `isCSIIntermediate()`
- `isCSIFinal()`
- `csi()`
- `CSI`
- `ERASE_DISPLAY`
- `ERASE_LINE_REGION`
- `CursorStyle`
- `CURSOR_STYLES`
- `cursorUp()`
- `cursorDown()`
- `cursorForward()`
- `cursorBack()`
- `cursorTo()`
- `CURSOR_LEFT`
- `cursorPosition()`
- `CURSOR_HOME`
- `cursorMove()`
- `CURSOR_SAVE`
- `CURSOR_RESTORE`
- `eraseToEndOfLine()`
- `eraseToStartOfLine()`
- `eraseLine()`
- ... +19 more

**Dependencies:** `./ansi`

**Main flow:** Entry: `isCSIParam()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/termio/dec.ts` (60 lines)

**Exports:**
- `DEC`
- `decset()`
- `decreset()`
- `BSU`
- `ESU`
- `EBP`
- `DBP`
- `EFE`
- `DFE`
- `SHOW_CURSOR`
- `HIDE_CURSOR`
- `ENTER_ALT_SCREEN`
- `EXIT_ALT_SCREEN`
- `ENABLE_MOUSE_TRACKING`
- `DISABLE_MOUSE_TRACKING`

**Dependencies:** `./csi`

**Main flow:** Entry: `decset()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/termio/esc.ts` (67 lines)

**Exports:**
- `parseEsc()`

**Dependencies:** `./types`

**Main flow:** Entry: `parseEsc()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/termio/osc.ts` (493 lines)

**Exports:**
- `OSC_PREFIX`
- `ST`
- `osc()`
- `wrapForMultiplexer()`
- `ClipboardPath`
- `getClipboardPath()`
- `tmuxLoadBuffer()`
- `setClipboard()`
- `_resetLinuxCopyCache()`
- `OSC`
- `parseOSC()`
- `parseOscColor()`
- `link()`
- `LINK_END`
- `ITERM2`
- `PROGRESS`
- `CLEAR_ITERM2_PROGRESS`
- `CLEAR_TERMINAL_TITLE`
- `CLEAR_TAB_STATUS`
- `supportsTabStatus()`
- `tabStatus()`

**Dependencies:** `buffer`, `../../utils/env`, `../../utils/execFileNoThrow`, `./ansi`, `./types`

**Main flow:** Entry: `osc()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/termio/parser.ts` (394 lines)

**Exports:**
- `Parser`

**Dependencies:** `../../utils/intl`, `./ansi`, `./csi`, `./dec`, `./esc`, `./osc`, `./sgr`, `./tokenize`, `./types`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/termio/sgr.ts` (308 lines)

**Exports:**
- `applySGR()`

**Dependencies:** `./types`

**Main flow:** Entry: `applySGR()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/termio/tokenize.ts` (319 lines)

**Exports:**
- `Token`
- `Tokenizer`
- `createTokenizer()`

**Dependencies:** `./ansi`, `./csi`

**Main flow:** Entry: `createTokenizer()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/termio/types.ts` (236 lines)

**Exports:**
- `NamedColor`
- `Color`
- `UnderlineStyle`
- `TextStyle`
- `defaultStyle()`
- `stylesEqual()`
- `colorsEqual()`
- `CursorDirection`
- `CursorAction`
- `EraseAction`
- `ScrollAction`
- `ModeAction`
- `LinkAction`
- `TitleAction`
- `TabStatusAction`
- `TextSegment`
- `Grapheme`
- `Action`

**Dependencies:** local only

**Main flow:** Entry: `defaultStyle()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/useTerminalNotification.ts` (126 lines)

**Exports:**
- `TerminalWriteContext`
- `TerminalWriteProvider`
- `TerminalNotification`
- `useTerminalNotification()`

**Dependencies:** `react`, `./terminal`, `./termio/ansi`, `./termio/osc`

**Main flow:** Entry: `useTerminalNotification()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/warn.ts` (9 lines)

**Exports:**
- `ifNotInteger()`

**Dependencies:** `../utils/debug`

**Main flow:** Entry: `ifNotInteger()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/widest-line.ts` (19 lines)

**Exports:**
- `widestLine()`

**Dependencies:** `./line-width-cache`

**Main flow:** Entry: `widestLine()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/wrap-text.ts` (74 lines)

**Exports:**
- default `wrapText()`

**Dependencies:** `../utils/sliceAnsi`, `./stringWidth`, `./styles`, `./wrapAnsi`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `ink/wrapAnsi.ts` (20 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `wrap-ansi`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `keybindings/KeybindingContext.tsx` (243 lines)

**Exports:**
- `KeybindingProvider()`
- `useKeybindingContext()`
- `useOptionalKeybindingContext()`
- `useRegisterKeybindingContext()`

**Dependencies:** `react/compiler-runtime`, `react`, `../ink`, `./resolver`, `./types`

**Main flow:** Entry: `KeybindingProvider()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `keybindings/KeybindingProviderSetup.tsx` (308 lines)

**Exports:**
- `KeybindingSetup()`

**Dependencies:** `react/compiler-runtime`, `react`, `../context/notifications`, `../ink/events/input-event`, `../ink`, `../utils/array`, `../utils/debug`, `../utils/stringUtils`, `./KeybindingContext`, `./loadUserBindings`

**Main flow:** Entry: `KeybindingSetup()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `keybindings/defaultBindings.ts` (340 lines)

**Exports:**
- `DEFAULT_BINDINGS`

**Dependencies:** `bun:bundle`, `src/utils/semver`, `../utils/bundledMode`, `../utils/platform`, `./types`

**Feature gates:** `KAIROS`, `KAIROS_BRIEF`, `MESSAGE_ACTIONS`, `QUICK_SEARCH`, `TERMINAL_PANEL`, `VOICE_MODE`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `keybindings/loadUserBindings.ts` (472 lines)

**Exports:**
- `isKeybindingCustomizationEnabled()`
- `KeybindingsLoadResult`
- `getKeybindingsPath()`
- `loadKeybindings()`
- `loadKeybindingsSync()`
- `loadKeybindingsSyncWithWarnings()`
- `initializeKeybindingWatcher()`
- `disposeKeybindingWatcher()`
- `subscribeToKeybindingChanges`
- `getCachedKeybindingWarnings()`
- `resetKeybindingLoaderForTesting()`

**Dependencies:** `chokidar`, `fs`, `fs/promises`, `path`, `../services/analytics/growthbook`, `../services/analytics/index`, `../utils/cleanupRegistry`, `../utils/debug`, `../utils/envUtils`, `../utils/errors`

**Main flow:** Entry: `isKeybindingCustomizationEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `keybindings/match.ts` (120 lines)

**Exports:**
- `getKeyName()`
- `matchesKeystroke()`
- `matchesBinding()`

**Dependencies:** `../ink`, `./types`

**Main flow:** Entry: `getKeyName()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `keybindings/parser.ts` (203 lines)

**Exports:**
- `parseKeystroke()`
- `parseChord()`
- `keystrokeToString()`
- `chordToString()`
- `keystrokeToDisplayString()`
- `chordToDisplayString()`
- `parseBindings()`

**Dependencies:** local only

**Main flow:** Entry: `parseKeystroke()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `keybindings/reservedShortcuts.ts` (127 lines)

**Exports:**
- `ReservedShortcut`
- `NON_REBINDABLE`
- `TERMINAL_RESERVED`
- `MACOS_RESERVED`
- `getReservedShortcuts()`
- `normalizeKeyForComparison()`

**Dependencies:** `../utils/platform`

**Main flow:** Entry: `getReservedShortcuts()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `keybindings/resolver.ts` (244 lines)

**Exports:**
- `ResolveResult`
- `ChordResolveResult`
- `resolveKey()`
- `getBindingDisplayText()`
- `keystrokesEqual()`
- `resolveKeyWithChordState()`

**Dependencies:** `../ink`, `./match`, `./parser`

**Main flow:** Entry: `resolveKey()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `keybindings/schema.ts` (236 lines)

**Exports:**
- `KEYBINDING_CONTEXTS`
- `KEYBINDING_CONTEXT_DESCRIPTIONS`
- `KEYBINDING_ACTIONS`
- `KeybindingBlockSchema`
- `KeybindingsSchema`
- `KeybindingsSchemaType`

**Dependencies:** `zod/v4`, `../utils/lazySchema`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `keybindings/shortcutFormat.ts` (63 lines)

**Exports:**
- `getShortcutDisplay()`

**Dependencies:** `./loadUserBindings`, `./resolver`, `./types`

**Main flow:** Entry: `getShortcutDisplay()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `keybindings/template.ts` (52 lines)

**Exports:**
- `generateKeybindingsTemplate()`

**Dependencies:** `../utils/slowOperations`, `./defaultBindings`, `./types`

**Main flow:** Entry: `generateKeybindingsTemplate()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `keybindings/useKeybinding.ts` (196 lines)

**Exports:**
- `useKeybinding()`
- `useKeybindings()`

**Dependencies:** `react`, `../ink/events/input-event`, `../ink`, `./KeybindingContext`, `./types`

**Main flow:** Entry: `useKeybinding()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `keybindings/useShortcutDisplay.ts` (59 lines)

**Exports:**
- `useShortcutDisplay()`

**Dependencies:** `react`, `./KeybindingContext`, `./types`

**Main flow:** Entry: `useShortcutDisplay()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `keybindings/validate.ts` (498 lines)

**Exports:**
- `KeybindingWarningType`
- `KeybindingWarning`
- `checkDuplicateKeysInJson()`
- `validateUserConfig()`
- `checkDuplicates()`
- `checkReservedShortcuts()`
- `validateBindings()`
- `formatWarning()`
- `formatWarnings()`

**Dependencies:** `../utils/stringUtils`, `./parser`

**Main flow:** Entry: `checkDuplicateKeysInJson()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `main.tsx` (4684 lines)

**Exports:**
- `startDeferredPrefetches()`
- `main()`

**Dependencies:** `./utils/startupProfiler`, `./utils/settings/mdm/rawRead`, `./utils/secureStorage/keychainPrefetch`, `bun:bundle`, `@commander-js/extra-typings`, `chalk`, `fs`, `lodash-es/mapValues`, `lodash-es/pickBy`, `lodash-es/uniqBy`

**Feature gates:** `AGENT_MEMORY_SNAPSHOT`, `BG_SESSIONS`, `BRIDGE_MODE`, `CCR_MIRROR`, `CHICAGO_MCP`, `COORDINATOR_MODE` (+12 more)

**Main flow:** Entry: `startDeferredPrefetches()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `memdir/findRelevantMemories.ts` (141 lines)

**Exports:**
- `RelevantMemory`
- `findRelevantMemories()`

**Dependencies:** `bun:bundle`, `../utils/debug`, `../utils/errors`, `../utils/model/model`, `../utils/sideQuery`, `../utils/slowOperations`

**Feature gates:** `MEMORY_SHAPE_TELEMETRY`

**Main flow:** Entry: `findRelevantMemories()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `memdir/memdir.ts` (507 lines)

**Exports:**
- `ENTRYPOINT_NAME`
- `MAX_ENTRYPOINT_LINES`
- `MAX_ENTRYPOINT_BYTES`
- `EntrypointTruncation`
- `truncateEntrypointContent()`
- `DIR_EXISTS_GUIDANCE`
- `DIRS_EXIST_GUIDANCE`
- `ensureMemoryDirExists()`
- `buildMemoryLines()`
- `buildMemoryPrompt()`
- `buildSearchingPastContextSection()`
- `loadMemoryPrompt()`

**Dependencies:** `bun:bundle`, `path`, `../utils/fsOperations`, `./paths`, `../bootstrap/state`, `../services/analytics/growthbook`, `../tools/GrepTool/prompt`, `../tools/REPLTool/constants`, `../utils/debug`, `../utils/embeddedTools`

**Feature gates:** `KAIROS`, `TEAMMEM`

**Main flow:** Entry: `truncateEntrypointContent()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `memdir/memoryAge.ts` (53 lines)

**Exports:**
- `memoryAgeDays()`
- `memoryAge()`
- `memoryFreshnessText()`
- `memoryFreshnessNote()`

**Dependencies:** local only

**Main flow:** Entry: `memoryAgeDays()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `memdir/memoryScan.ts` (94 lines)

**Exports:**
- `MemoryHeader`
- `scanMemoryFiles()`
- `formatMemoryManifest()`

**Dependencies:** `fs/promises`, `path`, `../utils/frontmatterParser`, `../utils/readFileInRange`, `./memoryTypes`

**Main flow:** Entry: `scanMemoryFiles()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `memdir/memoryTypes.ts` (271 lines)

**Exports:**
- `MEMORY_TYPES`
- `MemoryType`
- `parseMemoryType()`
- `TYPES_SECTION_COMBINED`
- `TYPES_SECTION_INDIVIDUAL`
- `WHAT_NOT_TO_SAVE_SECTION`
- `MEMORY_DRIFT_CAVEAT`
- `WHEN_TO_ACCESS_SECTION`
- `TRUSTING_RECALL_SECTION`
- `MEMORY_FRONTMATTER_EXAMPLE`

**Dependencies:** local only

**Main flow:** Entry: `parseMemoryType()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `memdir/paths.ts` (278 lines)

**Exports:**
- `isAutoMemoryEnabled()`
- `isExtractModeActive()`
- `getMemoryBaseDir()`
- `hasAutoMemPathOverride()`
- `getAutoMemPath`
- `getAutoMemDailyLogPath()`
- `getAutoMemEntrypoint()`
- `isAutoMemPath()`

**Dependencies:** `lodash-es/memoize`, `os`, `path`, `../services/analytics/growthbook`, `../utils/git`, `../utils/path`

**Feature gates:** `EXTRACT_MEMORIES`, `KAIROS`

**Main flow:** Entry: `isAutoMemoryEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `memdir/teamMemPaths.ts` (292 lines)

**Exports:**
- `PathTraversalError`
- `isTeamMemoryEnabled()`
- `getTeamMemPath()`
- `getTeamMemEntrypoint()`
- `isTeamMemPath()`
- `validateTeamMemWritePath()`
- `validateTeamMemKey()`
- `isTeamMemFile()`

**Dependencies:** `fs/promises`, `path`, `../services/analytics/growthbook`, `../utils/errors`, `./paths`

**Main flow:** Entry: `isTeamMemoryEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `memdir/teamMemPrompts.ts` (100 lines)

**Exports:**
- `buildCombinedMemoryPrompt()`

**Dependencies:** `./paths`, `./teamMemPaths`

**Main flow:** Entry: `buildCombinedMemoryPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `migrations/migrateAutoUpdatesToSettings.ts` (61 lines)

**Exports:**
- `migrateAutoUpdatesToSettings()`

**Dependencies:** `src/services/analytics/index`, `../utils/config`, `../utils/log`

**Main flow:** Entry: `migrateAutoUpdatesToSettings()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `migrations/migrateBypassPermissionsAcceptedToSettings.ts` (40 lines)

**Exports:**
- `migrateBypassPermissionsAcceptedToSettings()`

**Dependencies:** `src/services/analytics/index`, `../utils/config`, `../utils/log`

**Main flow:** Entry: `migrateBypassPermissionsAcceptedToSettings()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `migrations/migrateEnableAllProjectMcpServersToSettings.ts` (118 lines)

**Exports:**
- `migrateEnableAllProjectMcpServersToSettings()`

**Dependencies:** `src/services/analytics/index`, `../utils/log`

**Main flow:** Entry: `migrateEnableAllProjectMcpServersToSettings()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `migrations/migrateFennecToOpus.ts` (45 lines)

**Exports:**
- `migrateFennecToOpus()`

**Dependencies:** local only

**Main flow:** Entry: `migrateFennecToOpus()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `migrations/migrateLegacyOpusToCurrent.ts` (57 lines)

**Exports:**
- `migrateLegacyOpusToCurrent()`

**Dependencies:** `../utils/config`, `../utils/model/model`, `../utils/model/providers`

**Main flow:** Entry: `migrateLegacyOpusToCurrent()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `migrations/migrateOpusToOpus1m.ts` (43 lines)

**Exports:**
- `migrateOpusToOpus1m()`

**Dependencies:** `../services/analytics/index`

**Main flow:** Entry: `migrateOpusToOpus1m()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `migrations/migrateReplBridgeEnabledToRemoteControlAtStartup.ts` (22 lines)

**Exports:**
- `migrateReplBridgeEnabledToRemoteControlAtStartup()`

**Dependencies:** `../utils/config`

**Main flow:** Entry: `migrateReplBridgeEnabledToRemoteControlAtStartup()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `migrations/migrateSonnet1mToSonnet45.ts` (48 lines)

**Exports:**
- `migrateSonnet1mToSonnet45()`

**Dependencies:** `../utils/config`

**Main flow:** Entry: `migrateSonnet1mToSonnet45()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `migrations/migrateSonnet45ToSonnet46.ts` (67 lines)

**Exports:**
- `migrateSonnet45ToSonnet46()`

**Dependencies:** `../utils/config`, `../utils/model/providers`

**Main flow:** Entry: `migrateSonnet45ToSonnet46()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `migrations/resetAutoModeOptInForDefaultOffer.ts` (51 lines)

**Exports:**
- `resetAutoModeOptInForDefaultOffer()`

**Dependencies:** `bun:bundle`, `src/services/analytics/index`, `../utils/config`, `../utils/log`, `../utils/permissions/permissionSetup`

**Feature gates:** `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `resetAutoModeOptInForDefaultOffer()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `migrations/resetProToOpusDefault.ts` (51 lines)

**Exports:**
- `resetProToOpusDefault()`

**Dependencies:** `src/services/analytics/index`, `../utils/auth`, `../utils/config`, `../utils/model/providers`, `../utils/settings/settings`

**Main flow:** Entry: `resetProToOpusDefault()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `moreright/useMoreRight.tsx` (26 lines)

**Exports:**
- `useMoreRight()`

**Dependencies:** local only

**Main flow:** Entry: `useMoreRight()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `native-ts/color-diff/index.ts` (999 lines)

**Exports:**
- `Hunk`
- `SyntaxTheme`
- `NativeModule`
- `ColorDiff`
- `ColorFile`
- `getSyntaxTheme()`
- `getNativeModule()`
- `__test`

**Dependencies:** `diff`, `highlight`, `path`, `../../ink/stringWidth`, `../../utils/log`

**Main flow:** Entry: `getSyntaxTheme()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `native-ts/file-index/index.ts` (370 lines)

**Exports:**
- `SearchResult`
- `FileIndex`
- `yieldToEventLoop()`

**Dependencies:** local only

**Main flow:** Entry: `yieldToEventLoop()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `native-ts/yoga-layout/enums.ts` (134 lines)

**Exports:**
- `Align`
- `Align`
- `BoxSizing`
- `BoxSizing`
- `Dimension`
- `Dimension`
- `Direction`
- `Direction`
- `Display`
- `Display`
- `Edge`
- `Edge`
- `Errata`
- `Errata`
- `ExperimentalFeature`
- `ExperimentalFeature`
- `FlexDirection`
- `FlexDirection`
- `Gutter`
- `Gutter`
- `Justify`
- `Justify`
- `MeasureMode`
- `MeasureMode`
- `Overflow`
- ... +7 more

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `native-ts/yoga-layout/index.ts` (2578 lines)

**Exports:**
- `Value`
- `MeasureFunction`
- `Size`
- `Config`
- `Node`
- `getYogaCounters()`
- `Yoga`
- `loadYoga()`

**Dependencies:** local only

**Main flow:** Entry: `getYogaCounters()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `outputStyles/loadOutputStylesDir.ts` (98 lines)

**Exports:**
- `getOutputStyleDirStyles`
- `clearOutputStyleCaches()`

**Dependencies:** `lodash-es/memoize`, `path`, `../constants/outputStyles`, `../utils/debug`, `../utils/frontmatterParser`, `../utils/log`, `../utils/plugins/loadPluginOutputStyles`

**Main flow:** Entry: `clearOutputStyleCaches()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `query.ts` (1729 lines)

**Exports:**
- `QueryParams`

**Dependencies:** `./hooks/useCanUseTool`, `./services/api/withRetry`, `./services/compact/compact`, `./utils/imageValidation`, `./utils/imageResizer`, `./Tool`, `./utils/systemPromptType`, `./utils/log`, `./utils/debug`

**Feature gates:** `BG_SESSIONS`, `CACHED_MICROCOMPACT`, `CHICAGO_MCP`, `CONTEXT_COLLAPSE`, `EXPERIMENTAL_SKILL_SEARCH`, `HISTORY_SNIP` (+3 more)

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `query/config.ts` (46 lines)

**Exports:**
- `QueryConfig`
- `buildQueryConfig()`

**Dependencies:** `../bootstrap/state`, `../services/analytics/growthbook`, `../types/ids`, `../utils/envUtils`

**Main flow:** Entry: `buildQueryConfig()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `query/deps.ts` (40 lines)

**Exports:**
- `QueryDeps`
- `productionDeps()`

**Dependencies:** `crypto`, `../services/api/claude`, `../services/compact/autoCompact`, `../services/compact/microCompact`

**Main flow:** Entry: `productionDeps()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `query/stopHooks.ts` (473 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `bun:bundle`, `../keybindings/shortcutFormat`, `../memdir/paths`, `../Tool`, `../types/hooks`, `../utils/attachments`, `../utils/debug`, `../utils/errors`, `../utils/hooks/postSamplingHooks`, `../utils/systemPromptType`

**Feature gates:** `CHICAGO_MCP`, `EXTRACT_MEMORIES`, `TEMPLATES`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `query/tokenBudget.ts` (93 lines)

**Exports:**
- `BudgetTracker`
- `createBudgetTracker()`
- `TokenBudgetDecision`
- `checkTokenBudget()`

**Dependencies:** `../utils/tokenBudget`

**Main flow:** Entry: `createBudgetTracker()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `remote/RemoteSessionManager.ts` (343 lines)

**Exports:**
- `RemotePermissionResponse`
- `RemoteSessionConfig`
- `RemoteSessionCallbacks`
- `RemoteSessionManager`
- `createRemoteSessionConfig()`

**Dependencies:** `../entrypoints/agentSdkTypes`, `../utils/debug`, `../utils/log`

**Main flow:** Entry: `createRemoteSessionConfig()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `remote/SessionsWebSocket.ts` (404 lines)

**Exports:**
- `SessionsWebSocketCallbacks`
- `SessionsWebSocket`

**Dependencies:** `crypto`, `../constants/oauth`, `../entrypoints/agentSdkTypes`, `../utils/debug`, `../utils/errors`, `../utils/log`, `../utils/mtls`, `../utils/proxy`, `../utils/slowOperations`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `remote/remotePermissionBridge.ts` (78 lines)

**Exports:**
- `createSyntheticAssistantMessage()`
- `createToolStub()`

**Dependencies:** `crypto`, `../entrypoints/sdk/controlTypes`, `../Tool`, `../types/message`, `../utils/slowOperations`

**Main flow:** Entry: `createSyntheticAssistantMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `remote/sdkMessageAdapter.ts` (302 lines)

**Exports:**
- `ConvertedMessage`
- `convertSDKMessage()`
- `isSessionEndMessage()`
- `isSuccessResult()`
- `getResultText()`

**Dependencies:** `../utils/debug`, `../utils/messages/mappers`, `../utils/messages`

**Main flow:** Entry: `convertSDKMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `schemas/hooks.ts` (222 lines)

**Exports:**
- `HookCommandSchema`
- `HookMatcherSchema`
- `HooksSchema`
- `HookCommand`
- `BashCommandHook`
- `PromptHook`
- `AgentHook`
- `HttpHook`
- `HookMatcher`
- `HooksSettings`

**Dependencies:** `src/entrypoints/agentSdkTypes`, `zod/v4`, `../utils/lazySchema`, `../utils/shell/shellProvider`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `screens/Doctor.tsx` (575 lines)

**Exports:**
- `Doctor()`

**Dependencies:** `react/compiler-runtime`, `figures`, `path`, `react`, `src/components/KeybindingWarnings`, `src/components/mcp/McpParsingWarnings`, `src/utils/context`, `src/utils/envUtils`, `src/utils/settings/constants`, `../bootstrap/state`

**Main flow:** Entry: `Doctor()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `screens/REPL.tsx` (5006 lines)

**Exports:**
- `Props`
- `Screen`
- `REPL()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `child_process`, `../bootstrap/state`, `../utils/tokenBudget`, `../utils/array`, `path`, `os`, `figures`, `../ink`

**Feature gates:** `AGENT_TRIGGERS`, `AWAY_SUMMARY`, `BG_SESSIONS`, `BRIDGE_MODE`, `BUDDY`, `COMMIT_ATTRIBUTION` (+11 more)

**Main flow:** Entry: `REPL()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `screens/ResumeConversation.tsx` (399 lines)

**Exports:**
- `ResumeConversation()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `path`, `react`, `src/hooks/useTerminalSize`, `../bootstrap/state`, `../commands`, `../components/LogSelector`, `../components/Spinner`, `../cost-tracker`

**Feature gates:** `CONTEXT_COLLAPSE`, `COORDINATOR_MODE`

**Main flow:** Entry: `ResumeConversation()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/AgentSummary/agentSummary.ts` (179 lines)

**Exports:**
- `startAgentSummarization()`

**Dependencies:** `../../Task`, `../../tasks/LocalAgentTask/LocalAgentTask`, `../../tools/AgentTool/runAgent`, `../../types/ids`, `../../utils/debug`, `../../utils/log`, `../../utils/messages`, `../../utils/sessionStorage`

**Main flow:** Entry: `startAgentSummarization()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/MagicDocs/magicDocs.ts` (254 lines)

**Exports:**
- `clearTrackedMagicDocs()`
- `detectMagicDocHeader()`
- `registerMagicDoc()`
- `initMagicDocs()`

**Dependencies:** `../../Tool`, `../../tools/AgentTool/loadAgentsDir`, `../../tools/AgentTool/runAgent`, `../../tools/FileEditTool/constants`, `../../utils/errors`, `../../utils/fileStateCache`, `../../utils/sequential`, `./prompts`

**Main flow:** Entry: `clearTrackedMagicDocs()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/MagicDocs/prompts.ts` (127 lines)

**Exports:**
- `buildMagicDocsUpdatePrompt()`

**Dependencies:** `path`, `../../utils/envUtils`, `../../utils/fsOperations`

**Main flow:** Entry: `buildMagicDocsUpdatePrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/SessionMemory/prompts.ts` (324 lines)

**Exports:**
- `DEFAULT_SESSION_MEMORY_TEMPLATE`
- `loadSessionMemoryTemplate()`
- `loadSessionMemoryPrompt()`
- `isSessionMemoryEmpty()`
- `buildSessionMemoryUpdatePrompt()`
- `truncateSessionMemoryForCompact()`

**Dependencies:** `fs/promises`, `path`, `../../services/tokenEstimation`, `../../utils/envUtils`, `../../utils/errors`, `../../utils/log`

**Main flow:** Entry: `loadSessionMemoryTemplate()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/SessionMemory/sessionMemory.ts` (495 lines)

**Exports:**
- `resetLastMemoryMessageUuid()`
- `shouldExtractMemory()`
- `initSessionMemory()`
- `ManualExtractionResult`
- `manuallyExtractSessionMemory()`
- `createMemoryFileCanUseTool()`

**Dependencies:** `fs/promises`, `lodash-es/memoize`, `../../bootstrap/state`, `../../constants/prompts`, `../../context`, `../../hooks/useCanUseTool`, `../../Tool`, `../../tools/FileEditTool/constants`, `../../types/message`, `../../utils/array`

**Main flow:** Entry: `resetLastMemoryMessageUuid()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/SessionMemory/sessionMemoryUtils.ts` (207 lines)

**Exports:**
- `SessionMemoryConfig`
- `DEFAULT_SESSION_MEMORY_CONFIG`
- `getLastSummarizedMessageId()`
- `setLastSummarizedMessageId()`
- `markExtractionStarted()`
- `markExtractionCompleted()`
- `waitForSessionMemoryExtraction()`
- `getSessionMemoryContent()`
- `setSessionMemoryConfig()`
- `getSessionMemoryConfig()`
- `recordExtractionTokenCount()`
- `isSessionMemoryInitialized()`
- `markSessionMemoryInitialized()`
- `hasMetInitializationThreshold()`
- `hasMetUpdateThreshold()`
- `getToolCallsBetweenUpdates()`
- `resetSessionMemoryState()`

**Dependencies:** `../../utils/errors`, `../../utils/fsOperations`, `../../utils/permissions/filesystem`, `../../utils/sleep`, `../analytics/index`

**Main flow:** Entry: `getLastSummarizedMessageId()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/analytics/config.ts` (38 lines)

**Exports:**
- `isAnalyticsDisabled()`
- `isFeedbackSurveyDisabled()`

**Dependencies:** `../../utils/envUtils`, `../../utils/privacyLevel`

**Main flow:** Entry: `isAnalyticsDisabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/analytics/datadog.ts` (307 lines)

**Exports:**
- `initializeDatadog`
- `shutdownDatadog()`
- `trackDatadogEvent()`

**Dependencies:** `axios`, `crypto`, `lodash-es/memoize`, `../../utils/config`, `../../utils/log`, `../../utils/model/model`, `../../utils/model/providers`, `../../utils/modelCost`, `./config`, `./metadata`

**Main flow:** Entry: `shutdownDatadog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/analytics/firstPartyEventLogger.ts` (449 lines)

**Exports:**
- `EventSamplingConfig`
- `getEventSamplingConfig()`
- `shouldSampleEvent()`
- `shutdown1PEventLogging()`
- `is1PEventLoggingEnabled()`
- `logEventTo1P()`
- `GrowthBookExperimentData`
- `logGrowthBookExperimentTo1P()`
- `initialize1PEventLogging()`
- `reinitialize1PEventLoggingIfConfigChanged()`

**Dependencies:** `@opentelemetry/api-logs`, `@opentelemetry/resources`, `crypto`, `lodash-es`, `../../utils/config`, `../../utils/debug`, `../../utils/log`, `../../utils/platform`, `../../utils/slowOperations`, `../../utils/startupProfiler`

**Main flow:** Entry: `getEventSamplingConfig()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/analytics/firstPartyEventLoggingExporter.ts` (806 lines)

**Exports:**
- `FirstPartyEventLoggingExporter`

**Dependencies:** `@opentelemetry/api`, `@opentelemetry/core`, `axios`, `crypto`, `fs/promises`, `path`, `src/utils/user`, `../../types/generated/events_mono/claude_code/v1/claude_code_internal_event`, `../../types/generated/events_mono/growthbook/v1/growthbook_experiment_event`, `../../utils/config`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/analytics/growthbook.ts` (1155 lines)

**Exports:**
- `GrowthBookUserAttributes`
- `onGrowthBookRefresh()`
- `hasGrowthBookEnvOverride()`
- `getAllGrowthBookFeatures()`
- `getGrowthBookConfigOverrides()`
- `setGrowthBookConfigOverride()`
- `clearGrowthBookConfigOverrides()`
- `getApiBaseUrlHost()`
- `initializeGrowthBook`
- `getFeatureValue_DEPRECATED()`
- `getFeatureValue_CACHED_MAY_BE_STALE()`
- `getFeatureValue_CACHED_WITH_REFRESH()`
- `checkStatsigFeatureGate_CACHED_MAY_BE_STALE()`
- `checkSecurityRestrictionGate()`
- `checkGate_CACHED_OR_BLOCKING()`
- `refreshGrowthBookAfterAuthChange()`
- `resetGrowthBook()`
- `refreshGrowthBookFeatures()`
- `setupPeriodicGrowthBookRefresh()`
- `stopPeriodicGrowthBookRefresh()`
- `getDynamicConfig_BLOCKS_ON_INIT()`
- `getDynamicConfig_CACHED_MAY_BE_STALE()`

**Dependencies:** `@growthbook/growthbook`, `lodash-es`, `../../constants/keys`, `../../utils/debug`, `../../utils/errors`, `../../utils/http`, `../../utils/log`, `../../utils/signal`, `../../utils/slowOperations`

**Main flow:** Entry: `onGrowthBookRefresh()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/analytics/index.ts` (173 lines)

**Exports:**
- `AnalyticsMetadata_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS`
- `AnalyticsMetadata_I_VERIFIED_THIS_IS_PII_TAGGED`
- `stripProtoFields()`
- `AnalyticsSink`
- `attachAnalyticsSink()`
- `logEvent()`
- `logEventAsync()`
- `_resetForTesting()`

**Dependencies:** local only

**Main flow:** Entry: `stripProtoFields()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/analytics/metadata.ts` (973 lines)

**Exports:**
- `AnalyticsMetadata_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS`
- `sanitizeToolNameForAnalytics()`
- `isToolDetailsLoggingEnabled()`
- `isAnalyticsToolDetailsLoggingEnabled()`
- `mcpToolDetailsForAnalytics()`
- `extractMcpToolDetails()`
- `extractSkillName()`
- `extractToolInputForTelemetry()`
- `getFileExtensionForAnalytics()`
- `getFileExtensionsFromBashCommand()`
- `EnvContext`
- `ProcessMetrics`
- `EventMetadata`
- `EnrichMetadataOptions`
- `getEventMetadata()`
- `FirstPartyEventLoggingCoreMetadata`
- `FirstPartyEventLoggingMetadata`
- `to1PEventFormat()`

**Dependencies:** `path`, `lodash-es/memoize`, `../../utils/env`, `../../utils/envDynamic`, `../../utils/betas`, `../../utils/model/model`, `../../utils/envUtils`, `../mcp/officialRegistry`, `../../utils/auth`, `../../utils/git`

**Feature gates:** `CHICAGO_MCP`, `COWORKER_TYPE_TELEMETRY`, `KAIROS`

**Main flow:** Entry: `sanitizeToolNameForAnalytics()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/analytics/sink.ts` (114 lines)

**Exports:**
- `initializeAnalyticsGates()`
- `initializeAnalyticsSink()`

**Dependencies:** `./datadog`, `./firstPartyEventLogger`, `./growthbook`, `./index`, `./sinkKillswitch`

**Main flow:** Entry: `initializeAnalyticsGates()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/analytics/sinkKillswitch.ts` (25 lines)

**Exports:**
- `SinkName`
- `isSinkKilled()`

**Dependencies:** `./growthbook`

**Main flow:** Entry: `isSinkKilled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/adminRequests.ts` (119 lines)

**Exports:**
- `AdminRequestType`
- `AdminRequestStatus`
- `AdminRequestSeatUpgradeDetails`
- `AdminRequestCreateParams`
- `AdminRequest`
- `createAdminRequest()`
- `getMyAdminRequests()`
- `checkAdminRequestEligibility()`

**Dependencies:** `axios`, `../../constants/oauth`, `../../utils/teleport/api`

**Main flow:** Entry: `createAdminRequest()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/bootstrap.ts` (141 lines)

**Exports:**
- `fetchBootstrapData()`

**Dependencies:** `axios`, `lodash-es/isEqual`, `zod`, `../../constants/oauth`, `../../utils/config`, `../../utils/debug`, `../../utils/http`, `../../utils/lazySchema`, `../../utils/log`, `../../utils/model/providers`

**Main flow:** Entry: `fetchBootstrapData()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/claude.ts` (3419 lines)

**Exports:**
- `getExtraBodyParams()`
- `getPromptCachingEnabled()`
- `getCacheControl()`
- `configureTaskBudgetParams()`
- `getAPIMetadata()`
- `verifyApiKey()`
- `userMessageToMessageParam()`
- `assistantMessageToMessageParam()`
- `Options`
- `queryModelWithoutStreaming()`
- `stripExcessMediaItems()`
- `cleanupStream()`
- `updateUsage()`
- `accumulateUsage()`
- `addCacheBreakpoints()`
- `buildSystemPromptBlocks()`
- `queryHaiku()`
- `queryWithModel()`
- `MAX_NON_STREAMING_TOKENS`
- `adjustParamsForNonStreaming()`
- `getMaxOutputTokensForModel()`

**Dependencies:** `@anthropic-ai/sdk/resources/index.mjs`, `@anthropic-ai/sdk/streaming.mjs`, `crypto`, `../../tools/AgentTool/loadAgentsDir`

**Feature gates:** `ANTI_DISTILLATION_CC`, `CACHED_MICROCOMPACT`, `CONNECTOR_TEXT`, `PROMPT_CACHE_BREAK_DETECTION`, `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `getExtraBodyParams()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/client.ts` (389 lines)

**Exports:**
- `getAnthropicClient()`
- `CLIENT_REQUEST_ID_HEADER`

**Dependencies:** `@anthropic-ai/sdk`, `crypto`, `google-auth-library`, `src/utils/http`, `src/utils/model/model`, `src/utils/proxy`, `../../constants/oauth`, `../../utils/debug`

**Main flow:** Entry: `getAnthropicClient()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/dumpPrompts.ts` (226 lines)

**Exports:**
- `getLastApiRequests()`
- `clearApiRequestCache()`
- `clearDumpState()`
- `clearAllDumpState()`
- `addApiRequestToCache()`
- `getDumpPromptsPath()`
- `createDumpPromptsFetch()`

**Dependencies:** `@anthropic-ai/sdk`, `crypto`, `fs`, `path`, `src/bootstrap/state`, `../../utils/envUtils`, `../../utils/slowOperations`

**Main flow:** Entry: `getLastApiRequests()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/emptyUsage.ts` (22 lines)

**Exports:**
- `EMPTY_USAGE`

**Dependencies:** `../../entrypoints/sdk/sdkUtilityTypes`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/errorUtils.ts` (260 lines)

**Exports:**
- `ConnectionErrorDetails`
- `extractConnectionErrorDetails()`
- `getSSLErrorHint()`
- `sanitizeAPIError()`
- `formatAPIError()`

**Dependencies:** `@anthropic-ai/sdk`

**Main flow:** Entry: `extractConnectionErrorDetails()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/errors.ts` (1207 lines)

**Exports:**
- `API_ERROR_MESSAGE_PREFIX`
- `startsWithApiErrorPrefix()`
- `PROMPT_TOO_LONG_ERROR_MESSAGE`
- `isPromptTooLongMessage()`
- `parsePromptTooLongTokenCounts()`
- `getPromptTooLongTokenGap()`
- `isMediaSizeError()`
- `isMediaSizeErrorMessage()`
- `CREDIT_BALANCE_TOO_LOW_ERROR_MESSAGE`
- `INVALID_API_KEY_ERROR_MESSAGE`
- `INVALID_API_KEY_ERROR_MESSAGE_EXTERNAL`
- `ORG_DISABLED_ERROR_MESSAGE_ENV_KEY_WITH_OAUTH`
- `ORG_DISABLED_ERROR_MESSAGE_ENV_KEY`
- `TOKEN_REVOKED_ERROR_MESSAGE`
- `CCR_AUTH_ERROR_MESSAGE`
- `REPEATED_529_ERROR_MESSAGE`
- `CUSTOM_OFF_SWITCH_MESSAGE`
- `API_TIMEOUT_ERROR_MESSAGE`
- `getPdfTooLargeErrorMessage()`
- `getPdfPasswordProtectedErrorMessage()`
- `getPdfInvalidErrorMessage()`
- `getImageTooLargeErrorMessage()`
- `getRequestTooLargeErrorMessage()`
- `OAUTH_ORG_NOT_ALLOWED_ERROR_MESSAGE`
- `getTokenRevokedErrorMessage()`
- ... +7 more

**Dependencies:** `src/constants/betas`, `src/entrypoints/agentSdkTypes`, `src/utils/model/modelStrings`, `src/utils/model/providers`, `../../bootstrap/state`, `../../utils/envUtils`, `../../utils/format`, `../../utils/imageResizer`, `../../utils/imageValidation`

**Main flow:** Entry: `startsWithApiErrorPrefix()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/filesApi.ts` (748 lines)

**Exports:**
- `File`
- `FilesApiConfig`
- `DownloadResult`
- `downloadFile()`
- `buildDownloadPath()`
- `downloadAndSaveFile()`
- `downloadSessionFiles()`
- `UploadResult`
- `uploadFile()`
- `uploadSessionFiles()`
- `FileMetadata`
- `listFilesCreatedAfter()`
- `parseFileSpecs()`

**Dependencies:** `axios`, `crypto`, `fs/promises`, `path`, `../../utils/array`, `../../utils/cwd`, `../../utils/debug`, `../../utils/errors`, `../../utils/log`, `../../utils/sleep`

**Main flow:** Entry: `downloadFile()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/firstTokenDate.ts` (60 lines)

**Exports:**
- `fetchAndStoreClaudeCodeFirstTokenDate()`

**Dependencies:** `axios`, `../../constants/oauth`, `../../utils/config`, `../../utils/http`, `../../utils/log`, `../../utils/userAgent`

**Main flow:** Entry: `fetchAndStoreClaudeCodeFirstTokenDate()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/grove.ts` (357 lines)

**Exports:**
- `AccountSettings`
- `GroveConfig`
- `ApiResult`
- `getGroveSettings`
- `markGroveNoticeViewed()`
- `updateGroveSettings()`
- `isQualifiedForGrove()`
- `getGroveNoticeConfig`
- `calculateShouldShowGrove()`
- `checkGroveForNonInteractive()`

**Dependencies:** `axios`, `lodash-es/memoize`, `src/utils/auth`, `src/utils/debug`, `src/utils/gracefulShutdown`, `src/utils/privacyLevel`, `src/utils/process`, `../../constants/oauth`, `../../utils/config`, `../../utils/log`

**Main flow:** Entry: `markGroveNoticeViewed()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/logging.ts` (788 lines)

**Exports:**
- `GlobalCacheStrategy`
- `logAPIQuery()`
- `logAPIError()`
- `logAPISuccessAndDuration()`

**Dependencies:** `bun:bundle`, `@anthropic-ai/sdk`, `src/Tool`, `src/types/connectorText`, `src/types/message`, `src/utils/debug`, `src/utils/effort`, `src/utils/log`, `src/utils/model/providers`, `src/utils/permissions/PermissionMode`

**Feature gates:** `CACHED_MICROCOMPACT`, `CONNECTOR_TEXT`

**Main flow:** Entry: `logAPIQuery()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/metricsOptOut.ts` (159 lines)

**Exports:**
- `checkMetricsEnabled()`
- `_clearMetricsEnabledCacheForTesting`

**Dependencies:** `axios`, `../../utils/auth`, `../../utils/config`, `../../utils/debug`, `../../utils/errors`, `../../utils/http`, `../../utils/log`, `../../utils/memoize`, `../../utils/privacyLevel`, `../../utils/userAgent`

**Main flow:** Entry: `checkMetricsEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/overageCreditGrant.ts` (137 lines)

**Exports:**
- `OverageCreditGrantInfo`
- `getCachedOverageCreditGrant()`
- `invalidateOverageCreditGrantCache()`
- `refreshOverageCreditGrantCache()`
- `formatGrantAmount()`

**Dependencies:** `axios`, `../../constants/oauth`, `../../utils/auth`, `../../utils/config`, `../../utils/log`, `../../utils/privacyLevel`, `../../utils/teleport/api`

**Main flow:** Entry: `getCachedOverageCreditGrant()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/promptCacheBreakDetection.ts` (727 lines)

**Exports:**
- `CACHE_TTL_1HOUR_MS`
- `PromptStateSnapshot`
- `recordPromptState()`
- `checkResponseForCacheBreak()`
- `notifyCacheDeletion()`
- `notifyCompaction()`
- `cleanupAgentTracking()`
- `resetPromptCacheBreakDetection()`

**Dependencies:** `@anthropic-ai/sdk/resources/beta/messages/messages.mjs`, `@anthropic-ai/sdk/resources/index.mjs`, `diff`, `fs/promises`, `path`, `src/types/ids`, `src/types/message`, `src/utils/debug`, `src/utils/hash`, `src/utils/log`

**Main flow:** Entry: `recordPromptState()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/referral.ts` (281 lines)

**Exports:**
- `fetchReferralEligibility()`
- `fetchReferralRedemptions()`
- `checkCachedPassesEligibility()`
- `formatCreditAmount()`
- `getCachedReferrerReward()`
- `getCachedRemainingPasses()`
- `fetchAndStorePassesEligibility()`
- `getCachedOrFetchPassesEligibility()`
- `prefetchPassesEligibility()`

**Dependencies:** `axios`, `../../constants/oauth`, `../../utils/config`, `../../utils/debug`, `../../utils/log`, `../../utils/privacyLevel`, `../../utils/teleport/api`

**Main flow:** Entry: `fetchReferralEligibility()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/sessionIngress.ts` (514 lines)

**Exports:**
- `appendSessionLog()`
- `getSessionLogs()`
- `getSessionLogsViaOAuth()`
- `getTeleportEvents()`
- `clearSession()`
- `clearAllSessions()`

**Dependencies:** `axios`, `crypto`, `../../constants/oauth`, `../../types/logs`, `../../utils/debug`, `../../utils/diagLogs`, `../../utils/envUtils`, `../../utils/log`, `../../utils/sequential`, `../../utils/sessionIngressAuth`

**Main flow:** Entry: `appendSessionLog()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/ultrareviewQuota.ts` (38 lines)

**Exports:**
- `UltrareviewQuotaResponse`
- `fetchUltrareviewQuota()`

**Dependencies:** `axios`, `../../constants/oauth`, `../../utils/auth`, `../../utils/debug`, `../../utils/teleport/api`

**Main flow:** Entry: `fetchUltrareviewQuota()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/usage.ts` (63 lines)

**Exports:**
- `RateLimit`
- `ExtraUsage`
- `Utilization`
- `fetchUtilization()`

**Dependencies:** `axios`, `../../constants/oauth`, `../../utils/http`, `../../utils/userAgent`, `../oauth/client`

**Main flow:** Entry: `fetchUtilization()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/api/withRetry.ts` (822 lines)

**Exports:**
- `BASE_DELAY_MS`
- `RetryContext`
- `CannotRetryError`
- `FallbackTriggeredError`
- `getRetryDelay()`
- `parseMaxTokensContextOverflowError()`
- `is529Error()`
- `getDefaultMaxRetries()`

**Dependencies:** `bun:bundle`, `@anthropic-ai/sdk`, `src/constants/querySource`, `src/types/message`, `src/utils/aws`, `src/utils/debug`, `src/utils/log`, `src/utils/messages`, `src/utils/model/providers`, `../../utils/envUtils`

**Feature gates:** `BASH_CLASSIFIER`, `UNATTENDED_RETRY`

**Main flow:** Entry: `getRetryDelay()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/awaySummary.ts` (74 lines)

**Exports:**
- `generateAwaySummary()`

**Dependencies:** `@anthropic-ai/sdk`, `../Tool`, `../types/message`, `../utils/debug`, `../utils/model/model`, `../utils/systemPromptType`, `./api/claude`, `./SessionMemory/sessionMemoryUtils`

**Main flow:** Entry: `generateAwaySummary()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/claudeAiLimits.ts` (515 lines)

**Exports:**
- `getRateLimitDisplayName()`
- `OverageDisabledReason`
- `ClaudeAILimits`
- `currentLimits`
- `getRawUtilization()`
- `statusListeners`
- `emitStatusChange()`
- `checkQuotaStatus()`
- `extractQuotaStatusFromHeaders()`
- `extractQuotaStatusFromError()`

**Dependencies:** `@anthropic-ai/sdk`, `@anthropic-ai/sdk/resources/index.mjs`, `lodash-es/isEqual`, `../bootstrap/state`, `../utils/auth`, `../utils/betas`, `../utils/config`, `../utils/log`, `../utils/model/model`, `../utils/privacyLevel`

**Main flow:** Entry: `getRateLimitDisplayName()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/claudeAiLimitsHook.ts` (23 lines)

**Exports:**
- `useClaudeAiLimits()`

**Dependencies:** `react`

**Main flow:** Entry: `useClaudeAiLimits()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/compact/apiMicrocompact.ts` (153 lines)

**Exports:**
- `ContextEditStrategy`
- `ContextManagementConfig`
- `getAPIContextManagement()`

**Dependencies:** `src/tools/FileEditTool/constants`, `src/tools/FileReadTool/prompt`, `src/tools/FileWriteTool/prompt`, `src/tools/GlobTool/prompt`, `src/tools/GrepTool/prompt`, `src/tools/NotebookEditTool/constants`, `src/tools/WebFetchTool/prompt`, `src/tools/WebSearchTool/prompt`, `src/utils/shell/shellToolUtils`, `../../utils/envUtils`

**Main flow:** Entry: `getAPIContextManagement()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/compact/autoCompact.ts` (351 lines)

**Exports:**
- `getEffectiveContextWindowSize()`
- `AutoCompactTrackingState`
- `AUTOCOMPACT_BUFFER_TOKENS`
- `WARNING_THRESHOLD_BUFFER_TOKENS`
- `ERROR_THRESHOLD_BUFFER_TOKENS`
- `MANUAL_COMPACT_BUFFER_TOKENS`
- `getAutoCompactThreshold()`
- `calculateTokenWarningState()`
- `isAutoCompactEnabled()`
- `shouldAutoCompact()`
- `autoCompactIfNeeded()`

**Dependencies:** `bun:bundle`, `src/bootstrap/state`, `../../bootstrap/state`, `../../constants/querySource`, `../../Tool`, `../../types/message`, `../../utils/config`, `../../utils/context`, `../../utils/debug`, `../../utils/envUtils`

**Feature gates:** `CONTEXT_COLLAPSE`, `PROMPT_CACHE_BREAK_DETECTION`, `REACTIVE_COMPACT`

**Main flow:** Entry: `getEffectiveContextWindowSize()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/compact/compact.ts` (1705 lines)

**Exports:**
- `POST_COMPACT_MAX_FILES_TO_RESTORE`
- `POST_COMPACT_TOKEN_BUDGET`
- `POST_COMPACT_MAX_TOKENS_PER_FILE`
- `POST_COMPACT_MAX_TOKENS_PER_SKILL`
- `POST_COMPACT_SKILLS_TOKEN_BUDGET`
- `stripImagesFromMessages()`
- `stripReinjectedAttachments()`
- `ERROR_MESSAGE_NOT_ENOUGH_MESSAGES`
- `truncateHeadForPTLRetry()`
- `ERROR_MESSAGE_PROMPT_TOO_LONG`
- `ERROR_MESSAGE_USER_ABORT`
- `ERROR_MESSAGE_INCOMPLETE_RESPONSE`
- `CompactionResult`
- `RecompactionInfo`
- `buildPostCompactMessages()`
- `annotateBoundaryWithPreservedSegment()`
- `mergeHookInstructions()`
- `compactConversation()`
- `partialCompactConversation()`
- `createCompactCanUseTool()`
- `createPostCompactFileAttachments()`
- `createPlanAttachmentIfNeeded()`
- `createSkillAttachmentIfNeeded()`
- `createPlanModeAttachmentIfNeeded()`
- `createAsyncAgentAttachmentsIfNeeded()`

**Dependencies:** `bun:bundle`, `crypto`, `lodash-es/uniqBy`, `@anthropic-ai/sdk`, `src/bootstrap/state`, `../../bootstrap/state`, `../../constants/querySource`, `../../hooks/useCanUseTool`, `../../Tool`, `../../tasks/LocalAgentTask/LocalAgentTask`

**Feature gates:** `EXPERIMENTAL_SKILL_SEARCH`, `KAIROS`, `PROMPT_CACHE_BREAK_DETECTION`

**Main flow:** Entry: `stripImagesFromMessages()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/compact/compactWarningHook.ts` (16 lines)

**Exports:**
- `useCompactWarningSuppression()`

**Dependencies:** `react`, `./compactWarningState`

**Main flow:** Entry: `useCompactWarningSuppression()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/compact/compactWarningState.ts` (18 lines)

**Exports:**
- `compactWarningStore`
- `suppressCompactWarning()`
- `clearCompactWarningSuppression()`

**Dependencies:** `../../state/store`

**Main flow:** Entry: `suppressCompactWarning()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/compact/grouping.ts` (63 lines)

**Exports:**
- `groupMessagesByApiRound()`

**Dependencies:** `../../types/message`

**Main flow:** Entry: `groupMessagesByApiRound()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/compact/microCompact.ts` (530 lines)

**Exports:**
- `TIME_BASED_MC_CLEARED_MESSAGE`
- `consumePendingCacheEdits()`
- `getPinnedCacheEdits()`
- `pinCacheEdits()`
- `markToolsSentToAPIState()`
- `resetMicrocompactState()`
- `estimateMessageTokens()`
- `PendingCacheEdits`
- `MicrocompactResult`
- `microcompactMessages()`
- `evaluateTimeBasedTrigger()`

**Dependencies:** `bun:bundle`, `@anthropic-ai/sdk/resources/index.mjs`, `../../constants/querySource`, `../../Tool`, `../../tools/FileEditTool/constants`, `../../tools/FileReadTool/prompt`, `../../tools/FileWriteTool/prompt`, `../../tools/GlobTool/prompt`, `../../tools/GrepTool/prompt`, `../../tools/WebFetchTool/prompt`

**Feature gates:** `CACHED_MICROCOMPACT`, `PROMPT_CACHE_BREAK_DETECTION`

**Main flow:** Entry: `consumePendingCacheEdits()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/compact/postCompactCleanup.ts` (77 lines)

**Exports:**
- `runPostCompactCleanup()`

**Dependencies:** `bun:bundle`, `../../constants/querySource`, `../../constants/systemPromptSections`, `../../context`, `../../tools/BashTool/bashPermissions`, `../../utils/classifierApprovals`, `../../utils/claudemd`, `../../utils/sessionStorage`, `../../utils/telemetry/betaSessionTracing`, `./microCompact`

**Feature gates:** `COMMIT_ATTRIBUTION`, `CONTEXT_COLLAPSE`

**Main flow:** Entry: `runPostCompactCleanup()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/compact/prompt.ts` (374 lines)

**Exports:**
- `getPartialCompactPrompt()`
- `getCompactPrompt()`
- `formatCompactSummary()`
- `getCompactUserSummaryMessage()`

**Dependencies:** `bun:bundle`, `../../types/message`

**Feature gates:** `KAIROS`, `PROACTIVE`

**Main flow:** Entry: `getPartialCompactPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/compact/sessionMemoryCompact.ts` (630 lines)

**Exports:**
- `SessionMemoryCompactConfig`
- `DEFAULT_SM_COMPACT_CONFIG`
- `setSessionMemoryCompactConfig()`
- `getSessionMemoryCompactConfig()`
- `resetSessionMemoryCompactConfig()`
- `hasTextBlocks()`
- `adjustIndexToPreserveAPIInvariants()`
- `calculateMessagesToKeepIndex()`
- `shouldUseSessionMemoryCompaction()`
- `trySessionMemoryCompaction()`

**Dependencies:** `../../types/ids`, `../../types/message`, `../../utils/debug`, `../../utils/envUtils`, `../../utils/errors`, `../../utils/model/model`, `../../utils/permissions/filesystem`, `../../utils/sessionStart`, `../../utils/sessionStorage`, `../../utils/tokens`

**Main flow:** Entry: `setSessionMemoryCompactConfig()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/compact/timeBasedMCConfig.ts` (43 lines)

**Exports:**
- `TimeBasedMCConfig`
- `getTimeBasedMCConfig()`

**Dependencies:** `../analytics/growthbook`

**Main flow:** Entry: `getTimeBasedMCConfig()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/diagnosticTracking.ts` (397 lines)

**Exports:**
- `Diagnostic`
- `DiagnosticFile`
- `DiagnosticTrackingService`
- `diagnosticTracker`

**Dependencies:** `figures`, `src/utils/log`, `../services/mcp/client`, `../services/mcp/types`, `../utils/errors`, `../utils/file`, `../utils/ide`, `../utils/slowOperations`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/internalLogging.ts` (90 lines)

**Exports:**
- `getContainerId`
- `logPermissionContextForAnts()`

**Dependencies:** `fs/promises`, `lodash-es/memoize`, `../Tool`, `../utils/slowOperations`

**Main flow:** Entry: `logPermissionContextForAnts()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/lsp/LSPClient.ts` (447 lines)

**Exports:**
- `LSPClient`
- `createLSPClient()`

**Dependencies:** `child_process`, `../../utils/debug`, `../../utils/errors`, `../../utils/log`, `../../utils/subprocessEnv`

**Main flow:** Entry: `createLSPClient()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/lsp/LSPDiagnosticRegistry.ts` (386 lines)

**Exports:**
- `PendingLSPDiagnostic`
- `registerPendingLSPDiagnostic()`
- `checkForLSPDiagnostics()`
- `clearAllLSPDiagnostics()`
- `resetAllLSPDiagnosticState()`
- `clearDeliveredDiagnosticsForFile()`
- `getPendingLSPDiagnosticCount()`

**Dependencies:** `crypto`, `lru-cache`, `../../utils/debug`, `../../utils/errors`, `../../utils/log`, `../../utils/slowOperations`, `../diagnosticTracking`

**Main flow:** Entry: `registerPendingLSPDiagnostic()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/lsp/LSPServerInstance.ts` (511 lines)

**Exports:**
- `LSPServerInstance`
- `createLSPServerInstance()`

**Dependencies:** `path`, `url`, `vscode-languageserver-protocol`, `../../utils/cwd`, `../../utils/debug`, `../../utils/errors`, `../../utils/log`, `../../utils/sleep`, `./LSPClient`, `./types`

**Main flow:** Entry: `createLSPServerInstance()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/lsp/LSPServerManager.ts` (420 lines)

**Exports:**
- `LSPServerManager`
- `createLSPServerManager()`

**Dependencies:** `path`, `url`, `../../utils/debug`, `../../utils/errors`, `../../utils/log`, `./config`, `./types`

**Main flow:** Entry: `createLSPServerManager()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/lsp/config.ts` (79 lines)

**Exports:**
- `getAllLspServers()`

**Dependencies:** `../../types/plugin`, `../../utils/debug`, `../../utils/errors`, `../../utils/log`, `../../utils/plugins/lspPluginIntegration`, `../../utils/plugins/pluginLoader`, `./types`

**Main flow:** Entry: `getAllLspServers()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/lsp/manager.ts` (289 lines)

**Exports:**
- `_resetLspManagerForTesting()`
- `getLspServerManager()`
- `getInitializationStatus()`
- `isLspConnected()`
- `waitForInitialization()`
- `initializeLspServerManager()`
- `reinitializeLspServerManager()`
- `shutdownLspServerManager()`

**Dependencies:** `../../utils/debug`, `../../utils/envUtils`, `../../utils/errors`, `../../utils/log`, `./passiveFeedback`

**Main flow:** Entry: `_resetLspManagerForTesting()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/lsp/passiveFeedback.ts` (328 lines)

**Exports:**
- `formatDiagnosticsForAttachment()`
- `HandlerRegistrationResult`
- `registerLSPNotificationHandlers()`

**Dependencies:** `url`, `vscode-languageserver-protocol`, `../../utils/debug`, `../../utils/errors`, `../../utils/log`, `../../utils/slowOperations`, `../diagnosticTracking`, `./LSPDiagnosticRegistry`, `./LSPServerManager`

**Main flow:** Entry: `formatDiagnosticsForAttachment()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/InProcessTransport.ts` (63 lines)

**Exports:**
- `createLinkedTransportPair()`

**Dependencies:** `@modelcontextprotocol/sdk/shared/transport`, `@modelcontextprotocol/sdk/types`

**Main flow:** Entry: `createLinkedTransportPair()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/MCPConnectionManager.tsx` (73 lines)

**Exports:**
- `useMcpReconnect()`
- `useMcpToggleEnabled()`
- `MCPConnectionManager()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../commands`, `../../Tool`, `./types`, `./useManageMCPConnections`

**Main flow:** Entry: `useMcpReconnect()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/SdkControlTransport.ts` (136 lines)

**Exports:**
- `SendMcpMessageCallback`
- `SdkControlClientTransport`
- `SdkControlServerTransport`

**Dependencies:** `@modelcontextprotocol/sdk/shared/transport`, `@modelcontextprotocol/sdk/types`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/auth.ts` (2465 lines)

**Exports:**
- `normalizeOAuthErrorBody()`
- `AuthenticationCancelledError`
- `getServerKey()`
- `hasMcpDiscoveryButNoToken()`
- `revokeServerTokens()`
- `clearServerTokensFromLocalStorage()`
- `performMCPOAuthFlow()`
- `wrapFetchWithStepUpDetection()`
- `ClaudeAuthProvider`
- `readClientSecret()`
- `saveMcpClientSecret()`
- `clearMcpClientConfig()`
- `getMcpClientConfig()`

**Dependencies:** `@modelcontextprotocol/sdk/shared/transport`, `axios`, `crypto`, `fs/promises`, `http`, `path`, `url`, `xss`, `../../constants/oauth`, `../../utils/browser`

**Main flow:** Entry: `normalizeOAuthErrorBody()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/channelAllowlist.ts` (76 lines)

**Exports:**
- `ChannelAllowlistEntry`
- `getChannelAllowlist()`
- `isChannelsEnabled()`
- `isChannelAllowlisted()`

**Dependencies:** `zod/v4`, `../../utils/lazySchema`, `../../utils/plugins/pluginIdentifier`, `../analytics/growthbook`

**Main flow:** Entry: `getChannelAllowlist()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/channelNotification.ts` (316 lines)

**Exports:**
- `ChannelMessageNotificationSchema`
- `CHANNEL_PERMISSION_METHOD`
- `ChannelPermissionNotificationSchema`
- `CHANNEL_PERMISSION_REQUEST_METHOD`
- `ChannelPermissionRequestParams`
- `wrapChannelMessage()`
- `getEffectiveChannelAllowlist()`
- `ChannelGateResult`
- `findChannelEntry()`
- `gateChannelServer()`

**Dependencies:** `@modelcontextprotocol/sdk/types`, `zod/v4`, `../../bootstrap/state`, `../../constants/xml`, `../../utils/lazySchema`, `../../utils/plugins/pluginIdentifier`, `../../utils/settings/settings`, `../../utils/xml`

**Feature gates:** `KAIROS`, `KAIROS_CHANNELS`

**Main flow:** Entry: `wrapChannelMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/channelPermissions.ts` (240 lines)

**Exports:**
- `isChannelPermissionRelayEnabled()`
- `ChannelPermissionResponse`
- `ChannelPermissionCallbacks`
- `PERMISSION_REPLY_RE`
- `shortRequestId()`
- `truncateForPreview()`
- `filterPermissionRelayClients()`
- `createChannelPermissionCallbacks()`

**Dependencies:** `../../utils/slowOperations`, `../analytics/growthbook`

**Main flow:** Entry: `isChannelPermissionRelayEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/claudeai.ts` (164 lines)

**Exports:**
- `fetchClaudeAIMcpConfigsIfEligible`
- `clearClaudeAIMcpConfigsCache()`
- `markClaudeAiMcpConnected()`
- `hasClaudeAiMcpEverConnected()`

**Dependencies:** `axios`, `lodash-es/memoize`, `src/constants/oauth`, `src/utils/auth`, `src/utils/config`, `src/utils/debug`, `src/utils/envUtils`, `./client`, `./normalization`, `./types`

**Main flow:** Entry: `clearClaudeAIMcpConfigsCache()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/client.ts` (3348 lines)

**Exports:**
- `McpAuthError`
- `McpToolCallError_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS`
- `isMcpSessionExpiredError()`
- `clearMcpAuthCache()`
- `createClaudeAiProxyFetch()`
- `wrapFetchWithTimeout()`
- `getMcpServerConnectionBatchSize()`
- `getServerCacheKey()`
- `connectToServer`
- `clearServerCache()`
- `ensureConnectedClient()`
- `areMcpConfigsEqual()`
- `mcpToolInputToAutoClassifierInput()`
- `fetchToolsForClient`
- `fetchResourcesForClient`
- `fetchCommandsForClient`
- `callIdeRpc()`
- `reconnectMcpServerImpl()`
- `getMcpToolsCommandsAndResources()`
- `prefetchAllMcpResources()`
- `transformResultContent()`
- `MCPResultType`
- `TransformedMCPResult`
- `inferCompactSchema()`
- `transformMCPResult()`
- ... +3 more

**Dependencies:** `bun:bundle`, `@modelcontextprotocol/sdk/client/index`, `@modelcontextprotocol/sdk/client/stdio`, `lodash-es/mapValues`, `lodash-es/memoize`, `lodash-es/zipObject`, `p-map`, `../../bootstrap/state`, `../../commands`, `../../constants/oauth`

**Feature gates:** `CHICAGO_MCP`, `MCP_SKILLS`

**Main flow:** Entry: `isMcpSessionExpiredError()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/config.ts` (1578 lines)

**Exports:**
- `getEnterpriseMcpFilePath()`
- `unwrapCcrProxyUrl()`
- `getMcpServerSignature()`
- `dedupPluginMcpServers()`
- `dedupClaudeAiMcpServers()`
- `filterMcpServersByPolicy()`
- `addMcpConfig()`
- `removeMcpConfig()`
- `getProjectMcpConfigsFromCwd()`
- `getMcpConfigsByScope()`
- `getMcpConfigByName()`
- `getClaudeCodeMcpConfigs()`
- `getAllMcpConfigs()`
- `parseMcpConfig()`
- `parseMcpConfigFromFilePath()`
- `doesEnterpriseMcpConfigExist`
- `shouldAllowManagedMcpServersOnly()`
- `areMcpConfigsAllowedWithEnterpriseMcpConfig()`
- `isMcpServerDisabled()`
- `setMcpServerEnabled()`

**Dependencies:** `bun:bundle`, `fs/promises`, `lodash-es/mapValues`, `lodash-es/memoize`, `path`, `src/utils/platform`, `../../types/plugin`, `../../utils/claudeInChrome/common`, `../../utils/cwd`

**Feature gates:** `CHICAGO_MCP`

**Main flow:** Entry: `getEnterpriseMcpFilePath()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/elicitationHandler.ts` (313 lines)

**Exports:**
- `ElicitationWaitingState`
- `ElicitationRequestEvent`
- `registerElicitationHandler()`
- `runElicitationHooks()`
- `runElicitationResultHooks()`

**Dependencies:** `@modelcontextprotocol/sdk/client/index`, `../../state/AppState`, `../../utils/log`, `../../utils/slowOperations`

**Main flow:** Entry: `registerElicitationHandler()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/envExpansion.ts` (38 lines)

**Exports:**
- `expandEnvVarsInString()`

**Dependencies:** local only

**Main flow:** Entry: `expandEnvVarsInString()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/headersHelper.ts` (138 lines)

**Exports:**
- `getMcpHeadersFromHelper()`
- `getMcpServerHeaders()`

**Dependencies:** `../../bootstrap/state`, `../../utils/config`, `../../utils/debug`, `../../utils/errors`, `../../utils/execFileNoThrow`, `../../utils/log`, `../../utils/slowOperations`, `../analytics/index`

**Main flow:** Entry: `getMcpHeadersFromHelper()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/mcpStringUtils.ts` (106 lines)

**Exports:**
- `mcpInfoFromString()`
- `getMcpPrefix()`
- `buildMcpToolName()`
- `getToolNameForPermissionCheck()`
- `getMcpDisplayName()`
- `extractMcpToolDisplayName()`

**Dependencies:** `./normalization`

**Main flow:** Entry: `mcpInfoFromString()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/normalization.ts` (23 lines)

**Exports:**
- `normalizeNameForMCP()`

**Dependencies:** local only

**Main flow:** Entry: `normalizeNameForMCP()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/oauthPort.ts` (78 lines)

**Exports:**
- `buildRedirectUri()`
- `findAvailablePort()`

**Dependencies:** `http`, `../../utils/platform`

**Main flow:** Entry: `buildRedirectUri()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/officialRegistry.ts` (72 lines)

**Exports:**
- `prefetchOfficialMcpUrls()`
- `isOfficialMcpUrl()`
- `resetOfficialMcpUrlsForTesting()`

**Dependencies:** `axios`, `../../utils/debug`, `../../utils/errors`

**Main flow:** Entry: `prefetchOfficialMcpUrls()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/types.ts` (258 lines)

**Exports:**
- `ConfigScopeSchema`
- `ConfigScope`
- `TransportSchema`
- `Transport`
- `McpStdioServerConfigSchema`
- `McpSSEServerConfigSchema`
- `McpSSEIDEServerConfigSchema`
- `McpWebSocketIDEServerConfigSchema`
- `McpHTTPServerConfigSchema`
- `McpWebSocketServerConfigSchema`
- `McpSdkServerConfigSchema`
- `McpClaudeAIProxyServerConfigSchema`
- `McpServerConfigSchema`
- `McpStdioServerConfig`
- `McpSSEServerConfig`
- `McpSSEIDEServerConfig`
- `McpWebSocketIDEServerConfig`
- `McpHTTPServerConfig`
- `McpWebSocketServerConfig`
- `McpSdkServerConfig`
- `McpClaudeAIProxyServerConfig`
- `McpServerConfig`
- `ScopedMcpServerConfig`
- `McpJsonConfigSchema`
- `McpJsonConfig`
- ... +10 more

**Dependencies:** `@modelcontextprotocol/sdk/client/index`, `zod/v4`, `../../utils/lazySchema`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/useManageMCPConnections.ts` (1141 lines)

**Exports:**
- `useManageMCPConnections()`

**Dependencies:** `bun:bundle`, `path`, `react`, `../../bootstrap/state`, `../../commands`, `../../Tool`, `lodash-es/omit`, `lodash-es/reject`

**Feature gates:** `EXPERIMENTAL_SKILL_SEARCH`, `KAIROS`, `KAIROS_CHANNELS`, `MCP_SKILLS`

**Main flow:** Entry: `useManageMCPConnections()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/utils.ts` (575 lines)

**Exports:**
- `filterToolsByServer()`
- `commandBelongsToServer()`
- `filterCommandsByServer()`
- `filterMcpPromptsByServer()`
- `filterResourcesByServer()`
- `excludeToolsByServer()`
- `excludeCommandsByServer()`
- `excludeResourcesByServer()`
- `hashMcpConfig()`
- `excludeStalePluginClients()`
- `isToolFromMcpServer()`
- `isMcpTool()`
- `isMcpCommand()`
- `describeMcpConfigFilePath()`
- `getScopeLabel()`
- `ensureConfigScope()`
- `ensureTransport()`
- `parseHeaders()`
- `getProjectMcpServerStatus()`
- `getMcpServerScopeFromToolName()`
- `extractAgentMcpServers()`
- `getLoggingSafeMcpBaseUrl()`

**Dependencies:** `crypto`, `path`, `../../bootstrap/state`, `../../commands`, `../../components/mcp/types`, `../../Tool`, `../../tools/AgentTool/loadAgentsDir`, `../../utils/cwd`, `../../utils/env`, `../../utils/settings/constants`

**Main flow:** Entry: `filterToolsByServer()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/vscodeSdkMcp.ts` (112 lines)

**Exports:**
- `LogEventNotificationSchema`
- `notifyVscodeFileUpdated()`
- `setupVscodeSdkMcp()`

**Dependencies:** `src/utils/debug`, `zod/v4`, `../../utils/lazySchema`, `../analytics/index`, `./types`

**Main flow:** Entry: `notifyVscodeFileUpdated()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/xaa.ts` (511 lines)

**Exports:**
- `XaaTokenExchangeError`
- `ProtectedResourceMetadata`
- `discoverProtectedResource()`
- `AuthorizationServerMetadata`
- `discoverAuthorizationServer()`
- `JwtAuthGrantResult`
- `requestJwtAuthorizationGrant()`
- `XaaTokenResult`
- `XaaResult`
- `exchangeJwtAuthGrant()`
- `XaaConfig`
- `performCrossAppAccess()`

**Dependencies:** `@modelcontextprotocol/sdk/shared/transport`, `zod/v4`, `../../utils/lazySchema`, `../../utils/log`, `../../utils/slowOperations`

**Main flow:** Entry: `discoverProtectedResource()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcp/xaaIdpLogin.ts` (487 lines)

**Exports:**
- `isXaaEnabled()`
- `XaaIdpSettings`
- `getXaaIdpSettings()`
- `IdpLoginOptions`
- `issuerKey()`
- `getCachedIdpIdToken()`
- `saveIdpIdTokenFromJwt()`
- `clearIdpIdToken()`
- `saveIdpClientSecret()`
- `getIdpClientSecret()`
- `clearIdpClientSecret()`
- `discoverOidc()`
- `acquireIdpIdToken()`

**Dependencies:** `crypto`, `http`, `url`, `xss`, `../../utils/browser`, `../../utils/envUtils`, `../../utils/errors`, `../../utils/log`, `../../utils/platform`, `../../utils/secureStorage/index`

**Main flow:** Entry: `isXaaEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mcpServerApproval.tsx` (41 lines)

**Exports:**
- `handleMcpjsonServerApprovals()`

**Dependencies:** `react`, `../components/MCPServerApprovalDialog`, `../components/MCPServerMultiselectDialog`, `../ink`, `../keybindings/KeybindingProviderSetup`, `../state/AppState`, `./mcp/config`, `./mcp/utils`

**Main flow:** Entry: `handleMcpjsonServerApprovals()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/mockRateLimits.ts` (882 lines)

**Exports:**
- `MockHeaderKey`
- `MockScenario`
- `setMockHeader()`
- `addExceededLimit()`
- `setMockEarlyWarning()`
- `clearMockEarlyWarning()`
- `setMockRateLimitScenario()`
- `getMockHeaderless429Message()`
- `getMockHeaders()`
- `getMockStatus()`
- `clearMockHeaders()`
- `applyMockHeaders()`
- `shouldProcessMockLimits()`
- `getCurrentMockScenario()`
- `getScenarioDescription()`
- `setMockSubscriptionType()`
- `getMockSubscriptionType()`
- `shouldUseMockSubscription()`
- `setMockBillingAccess()`
- `isMockFastModeRateLimitScenario()`
- `checkMockFastModeRateLimit()`

**Dependencies:** `../services/oauth/types`, `../utils/billing`, `./claudeAiLimits`

**Main flow:** Entry: `setMockHeader()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/notifier.ts` (156 lines)

**Exports:**
- `NotificationOptions`
- `sendNotification()`

**Dependencies:** `../ink/useTerminalNotification`, `../utils/config`, `../utils/env`, `../utils/execFileNoThrow`, `../utils/hooks`, `../utils/log`

**Main flow:** Entry: `sendNotification()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/preventSleep.ts` (165 lines)

**Exports:**
- `startPreventSleep()`
- `stopPreventSleep()`
- `forceStopPreventSleep()`

**Dependencies:** `child_process`, `../utils/cleanupRegistry`, `../utils/debug`

**Main flow:** Entry: `startPreventSleep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/rateLimitMessages.ts` (344 lines)

**Exports:**
- `RATE_LIMIT_ERROR_PREFIXES`
- `isRateLimitErrorMessage()`
- `RateLimitMessage`
- `getRateLimitMessage()`
- `getRateLimitErrorMessage()`
- `getRateLimitWarning()`
- `getUsingOverageText()`

**Dependencies:** `../utils/billing`, `../utils/format`, `./claudeAiLimits`

**Main flow:** Entry: `isRateLimitErrorMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/rateLimitMocking.ts` (144 lines)

**Exports:**
- `processRateLimitHeaders()`
- `shouldProcessRateLimits()`
- `checkMockRateLimitError()`
- `isMockRateLimitError()`

**Dependencies:** `@anthropic-ai/sdk`

**Main flow:** Entry: `processRateLimitHeaders()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/tokenEstimation.ts` (495 lines)

**Exports:**
- `countTokensWithAPI()`
- `countMessagesTokensWithAPI()`
- `roughTokenCountEstimation()`
- `bytesPerTokenForFileType()`
- `roughTokenCountEstimationForFileType()`
- `countTokensViaHaikuFallback()`
- `roughTokenCountEstimationForMessages()`
- `roughTokenCountEstimationForMessage()`

**Dependencies:** `@anthropic-ai/sdk`, `@anthropic-ai/sdk/resources/beta/messages/messages.mjs`, `@aws-sdk/client-bedrock-runtime`, `src/utils/model/providers`, `../constants/betas`, `../utils/attachments`, `../utils/betas`, `../utils/envUtils`, `../utils/log`, `../utils/messages`

**Main flow:** Entry: `countTokensWithAPI()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/tools/StreamingToolExecutor.ts` (530 lines)

**Exports:**
- `StreamingToolExecutor`

**Dependencies:** `@anthropic-ai/sdk/resources/index.mjs`, `../../hooks/useCanUseTool`, `../../Tool`, `../../tools/BashTool/toolName`, `../../types/message`, `../../utils/abortController`, `./toolExecution`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/tools/toolExecution.ts` (1745 lines)

**Exports:**
- `HOOK_TIMING_DISPLAY_THRESHOLD_MS`
- `classifyToolError()`
- `MessageUpdateLazy`
- `McpServerType`
- `buildSchemaNotSentHint()`

**Dependencies:** `bun:bundle`, `../../hooks/useCanUseTool`, `../../tools/BashTool/BashTool`, `../../tools/BashTool/bashPermissions`, `../../tools/BashTool/toolName`, `../../tools/FileEditTool/constants`, `../../tools/FileReadTool/prompt`, `../../tools/FileWriteTool/prompt`, `../../tools/NotebookEditTool/constants`, `../../tools/PowerShellTool/toolName`

**Feature gates:** `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `classifyToolError()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/tools/toolHooks.ts` (650 lines)

**Exports:**
- `PostToolUseHooksResult`
- `resolveHookPermissionDecision()`

**Dependencies:** `src/services/analytics/metadata`, `zod/v4`, `../../hooks/useCanUseTool`, `../../Tool`, `../../types/hooks`, `../../types/permissions`, `../../utils/attachments`, `../../utils/debug`, `../../utils/log`, `../../utils/permissions/permissions`

**Main flow:** Entry: `resolveHookPermissionDecision()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/tools/toolOrchestration.ts` (188 lines)

**Exports:**
- `MessageUpdate`

**Dependencies:** `@anthropic-ai/sdk/resources/index.mjs`, `../../hooks/useCanUseTool`, `../../Tool`, `../../types/message`, `../../utils/generators`, `./toolExecution`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/vcr.ts` (406 lines)

**Exports:**
- `withVCR()`
- `withTokenCountVCR()`

**Dependencies:** `@anthropic-ai/sdk/resources/beta/messages/messages.mjs`, `crypto`, `fs/promises`, `lodash-es/isPlainObject`, `lodash-es/mapValues`, `path`, `src/cost-tracker`, `src/utils/modelCost`, `../utils/cwd`, `../utils/env`

**Main flow:** Entry: `withVCR()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/voice.ts` (525 lines)

**Exports:**
- `_resetArecordProbeForTesting()`
- `_resetAlsaCardsForTesting()`
- `checkVoiceDependencies()`
- `RecordingAvailability`
- `requestMicrophonePermission()`
- `checkRecordingAvailability()`
- `startRecording()`
- `stopRecording()`

**Dependencies:** `child_process`, `fs/promises`, `../utils/debug`, `../utils/envUtils`, `../utils/log`, `../utils/platform`

**Main flow:** Entry: `_resetArecordProbeForTesting()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/voiceKeyterms.ts` (106 lines)

**Exports:**
- `splitIdentifier()`
- `getVoiceKeyterms()`

**Dependencies:** `path`, `../bootstrap/state`, `../utils/git`

**Main flow:** Entry: `splitIdentifier()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `services/voiceStreamSTT.ts` (544 lines)

**Exports:**
- `FINALIZE_TIMEOUTS_MS`
- `VoiceStreamCallbacks`
- `FinalizeSource`
- `VoiceStreamConnection`
- `isVoiceStreamAvailable()`
- `connectVoiceStream()`

**Dependencies:** `http`, `ws`, `../constants/oauth`, `../utils/debug`, `../utils/http`, `../utils/log`, `../utils/mtls`, `../utils/proxy`, `../utils/slowOperations`, `./analytics/growthbook`

**Feature gates:** `VOICE_MODE`

**Main flow:** Entry: `isVoiceStreamAvailable()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/bundled/batch.ts` (124 lines)

**Exports:**
- `registerBatchSkill()`

**Dependencies:** `../../tools/AgentTool/constants`, `../../tools/AskUserQuestionTool/prompt`, `../../tools/EnterPlanModeTool/constants`, `../../tools/ExitPlanModeTool/constants`, `../../tools/SkillTool/constants`, `../../utils/git`, `../bundledSkills`

**Main flow:** Entry: `registerBatchSkill()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/bundled/claudeApi.ts` (196 lines)

**Exports:**
- `registerClaudeApiSkill()`

**Dependencies:** `fs/promises`, `../../utils/cwd`, `../bundledSkills`

**Main flow:** Entry: `registerClaudeApiSkill()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/bundled/claudeApiContent.ts` (75 lines)

**Exports:**
- `SKILL_MODEL_VARS`
- `SKILL_PROMPT`
- `SKILL_FILES`

**Dependencies:** `./claude-api/csharp/claude-api.md`, `./claude-api/curl/examples.md`, `./claude-api/go/claude-api.md`, `./claude-api/java/claude-api.md`, `./claude-api/php/claude-api.md`, `./claude-api/python/agent-sdk/patterns.md`, `./claude-api/python/agent-sdk/README.md`, `./claude-api/python/claude-api/batches.md`, `./claude-api/python/claude-api/files-api.md`, `./claude-api/python/claude-api/README.md`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/bundled/claudeInChrome.ts` (34 lines)

**Exports:**
- `registerClaudeInChromeSkill()`

**Dependencies:** `@ant/claude-for-chrome-mcp`, `../../utils/claudeInChrome/prompt`, `../../utils/claudeInChrome/setup`, `../bundledSkills`

**Main flow:** Entry: `registerClaudeInChromeSkill()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/bundled/debug.ts` (103 lines)

**Exports:**
- `registerDebugSkill()`

**Dependencies:** `fs/promises`, `src/tools/AgentTool/built-in/claudeCodeGuideAgent`, `src/utils/settings/settings`, `../../utils/debug`, `../../utils/errors`, `../../utils/format`, `../bundledSkills`

**Main flow:** Entry: `registerDebugSkill()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/bundled/index.ts` (79 lines)

**Exports:**
- `initBundledSkills()`

**Dependencies:** `bun:bundle`, `src/utils/claudeInChrome/setup`, `./batch`, `./claudeInChrome`, `./debug`, `./keybindings`, `./loremIpsum`, `./remember`, `./simplify`, `./skillify`

**Feature gates:** `AGENT_TRIGGERS`, `AGENT_TRIGGERS_REMOTE`, `BUILDING_CLAUDE_APPS`, `KAIROS`, `KAIROS_DREAM`, `REVIEW_ARTIFACT` (+1 more)

**Main flow:** Entry: `initBundledSkills()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/bundled/keybindings.ts` (339 lines)

**Exports:**
- `registerKeybindingsSkill()`

**Dependencies:** `../../keybindings/defaultBindings`, `../../keybindings/loadUserBindings`, `../../keybindings/schema`, `../../utils/slowOperations`, `../bundledSkills`

**Main flow:** Entry: `registerKeybindingsSkill()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/bundled/loop.ts` (92 lines)

**Exports:**
- `registerLoopSkill()`

**Dependencies:** `../bundledSkills`

**Main flow:** Entry: `registerLoopSkill()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/bundled/loremIpsum.ts` (282 lines)

**Exports:**
- `registerLoremIpsumSkill()`

**Dependencies:** `../bundledSkills`

**Main flow:** Entry: `registerLoremIpsumSkill()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/bundled/remember.ts` (82 lines)

**Exports:**
- `registerRememberSkill()`

**Dependencies:** `../../memdir/paths`, `../bundledSkills`

**Main flow:** Entry: `registerRememberSkill()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/bundled/scheduleRemoteAgents.ts` (447 lines)

**Exports:**
- `registerScheduleRemoteAgentsSkill()`

**Dependencies:** `../../services/analytics/growthbook`, `../../services/mcp/types`, `../../services/policyLimits/index`, `../../Tool`, `../../tools/AskUserQuestionTool/prompt`, `../../tools/RemoteTriggerTool/prompt`, `../../utils/auth`, `../../utils/background/remote/preconditions`, `../../utils/debug`, `../../utils/git`

**Main flow:** Entry: `registerScheduleRemoteAgentsSkill()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/bundled/simplify.ts` (69 lines)

**Exports:**
- `registerSimplifySkill()`

**Dependencies:** `../../tools/AgentTool/constants`, `../bundledSkills`

**Main flow:** Entry: `registerSimplifySkill()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/bundled/skillify.ts` (197 lines)

**Exports:**
- `registerSkillifySkill()`

**Dependencies:** `../../services/SessionMemory/sessionMemoryUtils`, `../../types/message`, `../../utils/messages`, `../bundledSkills`

**Main flow:** Entry: `registerSkillifySkill()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/bundled/stuck.ts` (79 lines)

**Exports:**
- `registerStuckSkill()`

**Dependencies:** `../bundledSkills`

**Main flow:** Entry: `registerStuckSkill()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/bundled/updateConfig.ts` (475 lines)

**Exports:**
- `registerUpdateConfigSkill()`

**Dependencies:** `zod/v4`, `../../utils/settings/types`, `../../utils/slowOperations`, `../bundledSkills`

**Main flow:** Entry: `registerUpdateConfigSkill()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/bundled/verify.ts` (30 lines)

**Exports:**
- `registerVerifySkill()`

**Dependencies:** `../../utils/frontmatterParser`, `../bundledSkills`, `./verifyContent`

**Main flow:** Entry: `registerVerifySkill()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/bundled/verifyContent.ts` (13 lines)

**Exports:**
- `SKILL_MD`
- `SKILL_FILES`

**Dependencies:** `./verify/examples/cli.md`, `./verify/examples/server.md`, `./verify/SKILL.md`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/bundledSkills.ts` (220 lines)

**Exports:**
- `BundledSkillDefinition`
- `registerBundledSkill()`
- `getBundledSkills()`
- `clearBundledSkills()`
- `getBundledSkillExtractDir()`

**Dependencies:** `@anthropic-ai/sdk/resources/index.mjs`, `fs`, `fs/promises`, `path`, `../Tool`, `../types/command`, `../utils/debug`, `../utils/permissions/filesystem`, `../utils/settings/types`

**Main flow:** Entry: `registerBundledSkill()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/loadSkillsDir.ts` (1086 lines)

**Exports:**
- `LoadedFrom`
- `getSkillsPath()`
- `estimateSkillFrontmatterTokens()`
- `parseSkillFrontmatterFields()`
- `createSkillCommand()`
- `getSkillDirCommands`
- `clearSkillCaches()`
- `onDynamicSkillsLoaded()`
- `discoverSkillDirsForPaths()`
- `addSkillDirectories()`
- `getDynamicSkills()`
- `activateConditionalSkillsForPaths()`
- `getConditionalSkillCount()`
- `clearDynamicSkills()`

**Dependencies:** `fs/promises`, `ignore`, `lodash-es/memoize`, `../services/tokenEstimation`, `../types/command`, `../utils/debug`, `../utils/errors`, `../utils/fsOperations`, `../utils/git/gitignore`, `../utils/log`

**Main flow:** Entry: `getSkillsPath()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `skills/mcpSkillBuilders.ts` (44 lines)

**Exports:**
- `MCPSkillBuilders`
- `registerMCPSkillBuilders()`
- `getMCPSkillBuilders()`

**Dependencies:** local only

**Main flow:** Entry: `registerMCPSkillBuilders()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `state/AppState.tsx` (200 lines)

**Exports:**
- `AppStoreContext`
- `AppStateProvider()`
- `useAppState()`
- `useSetAppState()`
- `useAppStateStore()`
- `useAppStateMaybeOutsideOfProvider()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `react`, `../context/mailbox`, `../hooks/useSettingsChange`, `../utils/debug`, `../utils/permissions/permissionSetup`, `../utils/settings/applySettingsChange`, `../utils/settings/constants`, `./store`

**Feature gates:** `VOICE_MODE`

**Main flow:** Entry: `AppStateProvider()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `state/AppStateStore.ts` (569 lines)

**Exports:**
- `CompletionBoundary`
- `SpeculationResult`
- `SpeculationState`
- `IDLE_SPECULATION_STATE`
- `FooterItem`
- `AppState`
- `AppStateStore`
- `getDefaultAppState()`

**Dependencies:** `src/context/notifications`, `src/utils/todo/types`, `../bridge/bridgePermissionCallbacks`, `../commands`, `../services/mcp/channelPermissions`, `../services/mcp/elicitationHandler`, `../services/PromptSuggestion/promptSuggestion`, `../tasks/types`, `../tools/AgentTool/agentColorManager`, `../tools/AgentTool/loadAgentsDir`

**Feature gates:** `CHICAGO_MCP`

**Main flow:** Entry: `getDefaultAppState()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `state/onChangeAppState.ts` (171 lines)

**Exports:**
- `externalMetadataToAppState()`
- `onChangeAppState()`

**Dependencies:** `../bootstrap/state`, `../utils/config`, `../utils/errors`, `../utils/log`, `../utils/managedEnv`, `../utils/settings/settings`, `./AppStateStore`

**Main flow:** Entry: `externalMetadataToAppState()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `state/selectors.ts` (76 lines)

**Exports:**
- `getViewedTeammateTask()`
- `ActiveAgentForInput`
- `getActiveAgentForInput()`

**Dependencies:** `../tasks/InProcessTeammateTask/types`, `../tasks/LocalAgentTask/LocalAgentTask`, `./AppStateStore`

**Main flow:** Entry: `getViewedTeammateTask()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `state/store.ts` (34 lines)

**Exports:**
- `Store`
- `createStore()`

**Dependencies:** local only

**Main flow:** Entry: `createStore()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `state/teammateViewHelpers.ts` (141 lines)

**Exports:**
- `enterTeammateView()`
- `exitTeammateView()`
- `stopOrDismissAgent()`

**Dependencies:** `../services/analytics/index`, `../Task`, `../tasks/LocalAgentTask/LocalAgentTask`, `./AppState`

**Main flow:** Entry: `enterTeammateView()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tasks.ts` (39 lines)

**Exports:**
- `getAllTasks()`
- `getTaskByType()`

**Dependencies:** `bun:bundle`, `./Task`, `./tasks/DreamTask/DreamTask`, `./tasks/LocalAgentTask/LocalAgentTask`, `./tasks/LocalShellTask/LocalShellTask`, `./tasks/RemoteAgentTask/RemoteAgentTask`

**Feature gates:** `MONITOR_TOOL`, `WORKFLOW_SCRIPTS`

**Main flow:** Entry: `getAllTasks()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tasks/DreamTask/DreamTask.ts` (157 lines)

**Exports:**
- `DreamTurn`
- `DreamPhase`
- `DreamTaskState`
- `isDreamTask()`
- `registerDreamTask()`
- `addDreamTurn()`
- `completeDreamTask()`
- `failDreamTask()`
- `DreamTask`

**Dependencies:** `../../services/autoDream/consolidationLock`, `../../Task`, `../../utils/task/framework`

**Main flow:** Entry: `isDreamTask()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tasks/InProcessTeammateTask/InProcessTeammateTask.tsx` (126 lines)

**Exports:**
- `InProcessTeammateTask`
- `requestTeammateShutdown()`
- `appendTeammateMessage()`
- `injectUserMessageToTeammate()`
- `findTeammateTaskByAgentId()`
- `getAllInProcessTeammateTasks()`
- `getRunningTeammatesSorted()`

**Dependencies:** `../../Task`, `../../types/message`, `../../utils/debug`, `../../utils/messages`, `../../utils/swarm/spawnInProcess`, `../../utils/task/framework`, `./types`

**Main flow:** Entry: `requestTeammateShutdown()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tasks/InProcessTeammateTask/types.ts` (121 lines)

**Exports:**
- `TeammateIdentity`
- `InProcessTeammateTaskState`
- `isInProcessTeammateTask()`
- `TEAMMATE_MESSAGES_UI_CAP`
- `appendCappedMessage()`

**Dependencies:** `../../Task`, `../../tools/AgentTool/agentToolUtils`, `../../tools/AgentTool/loadAgentsDir`, `../../types/message`, `../../utils/permissions/PermissionMode`, `../LocalAgentTask/LocalAgentTask`

**Main flow:** Entry: `isInProcessTeammateTask()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tasks/LocalAgentTask/LocalAgentTask.tsx` (683 lines)

**Exports:**
- `ToolActivity`
- `AgentProgress`
- `ProgressTracker`
- `createProgressTracker()`
- `getTokenCountFromTracker()`
- `ActivityDescriptionResolver`
- `updateProgressFromMessage()`
- `getProgressUpdate()`
- `createActivityDescriptionResolver()`
- `LocalAgentTaskState`
- `isLocalAgentTask()`
- `isPanelAgentTask()`
- `queuePendingMessage()`
- `appendMessageToLocalAgent()`
- `drainPendingMessages()`
- `enqueueAgentNotification()`
- `LocalAgentTask`
- `killAsyncAgent()`
- `killAllRunningAgentTasks()`
- `markAgentsNotified()`
- `updateAgentProgress()`
- `updateAgentSummary()`
- `completeAgentTask()`
- `failAgentTask()`
- `registerAsyncAgent()`
- ... +3 more

**Dependencies:** `../../bootstrap/state`, `../../constants/xml`, `../../services/PromptSuggestion/speculation`, `../../state/AppState`, `../../Task`, `../../Tool`, `../../tools/AgentTool/agentToolUtils`, `../../tools/AgentTool/loadAgentsDir`

**Main flow:** Entry: `createProgressTracker()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tasks/LocalMainSessionTask.ts` (479 lines)

**Exports:**
- `LocalMainSessionTaskState`
- `registerMainSessionTask()`
- `completeMainSessionTask()`
- `foregroundMainSessionTask()`
- `isMainSessionTask()`
- `startBackgroundSession()`

**Dependencies:** `crypto`, `../query`, `../services/tokenEstimation`, `../Task`, `../types/ids`, `../types/message`, `../utils/abortController`, `../utils/cleanupRegistry`

**Main flow:** Entry: `registerMainSessionTask()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tasks/LocalShellTask/LocalShellTask.tsx` (523 lines)

**Exports:**
- `BACKGROUND_BASH_SUMMARY_PREFIX`
- `looksLikePrompt()`
- `LocalShellTask`
- `spawnShellTask()`
- `registerForeground()`
- `hasForegroundTasks()`
- `backgroundAll()`
- `backgroundExistingForegroundTask()`
- `markTaskNotified()`
- `unregisterForeground()`

**Dependencies:** `bun:bundle`, `fs/promises`, `../../constants/xml`, `../../services/PromptSuggestion/speculation`, `../../state/AppState`, `../../Task`, `../../types/ids`, `../../utils/cleanupRegistry`, `../../utils/fsOperations`

**Feature gates:** `MONITOR_TOOL`

**Main flow:** Entry: `looksLikePrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tasks/LocalShellTask/guards.ts` (41 lines)

**Exports:**
- `BashTaskKind`
- `LocalShellTaskState`
- `isLocalShellTask()`

**Dependencies:** `../../Task`, `../../types/ids`, `../../utils/ShellCommand`

**Main flow:** Entry: `isLocalShellTask()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tasks/LocalShellTask/killShellTasks.ts` (76 lines)

**Exports:**
- `killTask()`
- `killShellTasksForAgent()`

**Dependencies:** `../../state/AppState`, `../../types/ids`, `../../utils/debug`, `../../utils/log`, `../../utils/messageQueueManager`, `../../utils/task/diskOutput`, `../../utils/task/framework`, `./guards`

**Main flow:** Entry: `killTask()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tasks/RemoteAgentTask/RemoteAgentTask.tsx` (856 lines)

**Exports:**
- `RemoteAgentTaskState`
- `RemoteTaskType`
- `AutofixPrRemoteTaskMetadata`
- `RemoteTaskMetadata`
- `RemoteTaskCompletionChecker`
- `registerCompletionChecker()`
- `RemoteAgentPreconditionResult`
- `checkRemoteAgentEligibility()`
- `formatPreconditionError()`
- `extractPlanFromLog()`
- `enqueueUltraplanFailureNotification()`
- `registerRemoteAgentTask()`
- `restoreRemoteAgentTasks()`
- `RemoteAgentTask`
- `getRemoteTaskSessionUrl()`

**Dependencies:** `@anthropic-ai/sdk/resources`, `../../constants/product`, `../../constants/xml`, `../../entrypoints/agentSdkTypes`, `../../Task`, `../../tools/TodoWriteTool/TodoWriteTool`, `../../utils/background/remote/remoteSession`, `../../utils/debug`, `../../utils/log`

**Main flow:** Entry: `registerCompletionChecker()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tasks/pillLabel.ts` (82 lines)

**Exports:**
- `getPillLabel()`
- `pillNeedsCta()`

**Dependencies:** `../constants/figures`, `../utils/array`, `./types`

**Main flow:** Entry: `getPillLabel()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tasks/stopTask.ts` (100 lines)

**Exports:**
- `StopTaskError`
- `stopTask()`

**Dependencies:** `../state/AppState`, `../Task`, `../tasks`, `../utils/sdkEventQueue`, `./LocalShellTask/guards`

**Main flow:** Entry: `stopTask()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tasks/types.ts` (46 lines)

**Exports:**
- `TaskState`
- `BackgroundTaskState`
- `isBackgroundTask()`

**Dependencies:** `./DreamTask/DreamTask`, `./InProcessTeammateTask/types`, `./LocalAgentTask/LocalAgentTask`, `./LocalShellTask/guards`, `./LocalWorkflowTask/LocalWorkflowTask`, `./MonitorMcpTask/MonitorMcpTask`, `./RemoteAgentTask/RemoteAgentTask`

**Main flow:** Entry: `isBackgroundTask()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools.ts` (389 lines)

**Exports:**
- `TOOL_PRESETS`
- `ToolPreset`
- `parseToolPreset()`
- `getToolsForDefaultPreset()`
- `getAllBaseTools()`
- `filterToolsByDenyRules()`
- `getTools`
- `assembleToolPool()`
- `getMergedTools()`

**Dependencies:** `./Tool`, `./tools/AgentTool/AgentTool`, `./tools/SkillTool/SkillTool`, `./tools/BashTool/BashTool`, `./tools/FileEditTool/FileEditTool`, `./tools/FileReadTool/FileReadTool`, `./tools/FileWriteTool/FileWriteTool`, `./tools/GlobTool/GlobTool`, `./tools/NotebookEditTool/NotebookEditTool`, `./tools/WebFetchTool/WebFetchTool`

**Feature gates:** `AGENT_TRIGGERS`, `AGENT_TRIGGERS_REMOTE`, `CONTEXT_COLLAPSE`, `COORDINATOR_MODE`, `HISTORY_SNIP`, `KAIROS` (+9 more)

**Main flow:** Entry: `parseToolPreset()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/AgentTool.tsx` (1398 lines)

**Exports:**
- `inputSchema`
- `outputSchema`
- `RemoteLaunchedOutput`
- `Progress`
- `AgentTool`

**Dependencies:** `bun:bundle`, `react`, `src/Tool`, `src/types/message`, `src/utils/promptCategory`, `zod/v4`, `../../bootstrap/state`, `../../constants/prompts`, `../../coordinator/coordinatorMode`, `../../services/AgentSummary/agentSummary`

**Feature gates:** `COORDINATOR_MODE`, `KAIROS`, `PROACTIVE`, `TRANSCRIPT_CLASSIFIER`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/UI.tsx` (872 lines)

**Exports:**
- `AgentPromptDisplay()`
- `AgentResponseDisplay()`
- `renderToolResultMessage()`
- `renderToolUseMessage()`
- `renderToolUseTag()`
- `renderToolUseProgressMessage()`
- `renderToolUseRejectedMessage()`
- `renderToolUseErrorMessage()`
- `renderGroupedAgentToolUse()`
- `userFacingName()`
- `userFacingNameBackgroundColor()`
- `extractLastToolInfo()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/index.mjs`, `react`, `src/components/ConfigurableShortcutHint`, `src/components/CtrlOToExpand`, `src/components/design-system/Byline`, `src/components/design-system/KeyboardShortcutHint`, `zod/v4`, `../../components/AgentProgressLine`, `../../components/FallbackToolUseErrorMessage`

**Main flow:** Entry: `AgentPromptDisplay()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/agentColorManager.ts` (66 lines)

**Exports:**
- `AgentColorName`
- `AGENT_COLORS`
- `AGENT_COLOR_TO_THEME_COLOR`
- `getAgentColor()`
- `setAgentColor()`

**Dependencies:** `../../bootstrap/state`, `../../utils/theme`

**Main flow:** Entry: `getAgentColor()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/agentDisplay.ts` (104 lines)

**Exports:**
- `AgentSourceGroup`
- `AGENT_SOURCE_GROUPS`
- `ResolvedAgent`
- `resolveAgentOverrides()`
- `resolveAgentModelDisplay()`
- `getOverrideSourceLabel()`
- `compareAgentsByName()`

**Dependencies:** `../../utils/model/agent`, `./loadAgentsDir`

**Main flow:** Entry: `resolveAgentOverrides()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/agentMemory.ts` (177 lines)

**Exports:**
- `AgentMemoryScope`
- `getAgentMemoryDir()`
- `isAgentMemoryPath()`
- `getAgentMemoryEntrypoint()`
- `getMemoryScopeDisplay()`
- `loadAgentMemoryPrompt()`

**Dependencies:** `path`, `../../bootstrap/state`, `../../memdir/paths`, `../../utils/cwd`, `../../utils/git`, `../../utils/path`

**Main flow:** Entry: `getAgentMemoryDir()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/agentMemorySnapshot.ts` (197 lines)

**Exports:**
- `getSnapshotDirForAgent()`
- `checkAgentMemorySnapshot()`
- `initializeFromSnapshot()`
- `replaceFromSnapshot()`
- `markSnapshotSynced()`

**Dependencies:** `fs/promises`, `path`, `zod/v4`, `../../utils/cwd`, `../../utils/debug`, `../../utils/lazySchema`, `../../utils/slowOperations`, `./agentMemory`

**Main flow:** Entry: `getSnapshotDirForAgent()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/agentToolUtils.ts` (686 lines)

**Exports:**
- `ResolvedAgentTools`
- `filterToolsForAgent()`
- `resolveAgentTools()`
- `agentToolResultSchema`
- `AgentToolResult`
- `countToolUses()`
- `finalizeAgentTool()`
- `getLastToolUseName()`
- `emitTaskProgress()`
- `classifyHandoffIfNeeded()`
- `extractPartialResult()`
- `runAsyncAgentLifecycle()`

**Dependencies:** `bun:bundle`, `zod/v4`, `../../bootstrap/state`, `../../services/AgentSummary/agentSummary`, `../../services/api/dumpPrompts`, `../../state/AppState`, `../../Tool`, `../../types/ids`, `../../types/message`, `../../utils/agentSwarmsEnabled`

**Feature gates:** `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `filterToolsForAgent()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/built-in/claudeCodeGuideAgent.ts` (205 lines)

**Exports:**
- `CLAUDE_CODE_GUIDE_AGENT_TYPE`
- `CLAUDE_CODE_GUIDE_AGENT`

**Dependencies:** `src/tools/BashTool/toolName`, `src/tools/FileReadTool/prompt`, `src/tools/GlobTool/prompt`, `src/tools/GrepTool/prompt`, `src/tools/SendMessageTool/constants`, `src/tools/WebFetchTool/prompt`, `src/tools/WebSearchTool/prompt`, `src/utils/auth`, `src/utils/embeddedTools`, `src/utils/settings/settings`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/built-in/exploreAgent.ts` (83 lines)

**Exports:**
- `EXPLORE_AGENT_MIN_QUERIES`
- `EXPLORE_AGENT`

**Dependencies:** `src/tools/BashTool/toolName`, `src/tools/ExitPlanModeTool/constants`, `src/tools/FileEditTool/constants`, `src/tools/FileReadTool/prompt`, `src/tools/FileWriteTool/prompt`, `src/tools/GlobTool/prompt`, `src/tools/GrepTool/prompt`, `src/tools/NotebookEditTool/constants`, `src/utils/embeddedTools`, `../constants`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/built-in/generalPurposeAgent.ts` (34 lines)

**Exports:**
- `GENERAL_PURPOSE_AGENT`

**Dependencies:** `../loadAgentsDir`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/built-in/planAgent.ts` (92 lines)

**Exports:**
- `PLAN_AGENT`

**Dependencies:** `src/tools/BashTool/toolName`, `src/tools/ExitPlanModeTool/constants`, `src/tools/FileEditTool/constants`, `src/tools/FileReadTool/prompt`, `src/tools/FileWriteTool/prompt`, `src/tools/GlobTool/prompt`, `src/tools/GrepTool/prompt`, `src/tools/NotebookEditTool/constants`, `src/utils/embeddedTools`, `../constants`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/built-in/statuslineSetup.ts` (144 lines)

**Exports:**
- `STATUSLINE_SETUP_AGENT`

**Dependencies:** `../loadAgentsDir`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/built-in/verificationAgent.ts` (152 lines)

**Exports:**
- `VERIFICATION_AGENT`

**Dependencies:** `src/tools/BashTool/toolName`, `src/tools/ExitPlanModeTool/constants`, `src/tools/FileEditTool/constants`, `src/tools/FileWriteTool/prompt`, `src/tools/NotebookEditTool/constants`, `src/tools/WebFetchTool/prompt`, `../constants`, `../loadAgentsDir`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/builtInAgents.ts` (72 lines)

**Exports:**
- `areExplorePlanAgentsEnabled()`
- `getBuiltInAgents()`

**Dependencies:** `bun:bundle`, `../../bootstrap/state`, `../../services/analytics/growthbook`, `../../utils/envUtils`, `./built-in/claudeCodeGuideAgent`, `./built-in/exploreAgent`, `./built-in/generalPurposeAgent`, `./built-in/planAgent`, `./built-in/statuslineSetup`, `./built-in/verificationAgent`

**Feature gates:** `BUILTIN_EXPLORE_PLAN_AGENTS`, `COORDINATOR_MODE`, `VERIFICATION_AGENT`

**Main flow:** Entry: `areExplorePlanAgentsEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/constants.ts` (12 lines)

**Exports:**
- `AGENT_TOOL_NAME`
- `LEGACY_AGENT_TOOL_NAME`
- `VERIFICATION_AGENT_TYPE`
- `ONE_SHOT_BUILTIN_AGENT_TYPES`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/forkSubagent.ts` (210 lines)

**Exports:**
- `isForkSubagentEnabled()`
- `FORK_SUBAGENT_TYPE`
- `FORK_AGENT`
- `isInForkChild()`
- `buildForkedMessages()`
- `buildChildMessage()`
- `buildWorktreeNotice()`

**Dependencies:** `bun:bundle`, `@anthropic-ai/sdk/resources/beta/messages/messages.mjs`, `crypto`, `../../bootstrap/state`, `../../coordinator/coordinatorMode`, `../../utils/debug`, `../../utils/messages`, `./loadAgentsDir`

**Feature gates:** `FORK_SUBAGENT`

**Main flow:** Entry: `isForkSubagentEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/loadAgentsDir.ts` (755 lines)

**Exports:**
- `AgentMcpServerSpec`
- `BaseAgentDefinition`
- `BuiltInAgentDefinition`
- `CustomAgentDefinition`
- `PluginAgentDefinition`
- `AgentDefinition`
- `isBuiltInAgent()`
- `isCustomAgent()`
- `isPluginAgent()`
- `AgentDefinitionsResult`
- `getActiveAgentsFromList()`
- `hasRequiredMcpServers()`
- `filterAgentsByMcpRequirements()`
- `getAgentDefinitionsWithOverrides`
- `clearAgentDefinitionsCache()`
- `parseAgentFromJson()`
- `parseAgentsFromJson()`
- `parseAgentFromMarkdown()`

**Dependencies:** `bun:bundle`, `lodash-es/memoize`, `path`, `src/utils/settings/constants`, `zod/v4`, `../../memdir/paths`, `../../Tool`, `../../utils/debug`, `../../utils/envUtils`, `../../utils/frontmatterParser`

**Feature gates:** `AGENT_MEMORY_SNAPSHOT`

**Main flow:** Entry: `isBuiltInAgent()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/prompt.ts` (287 lines)

**Exports:**
- `formatAgentLine()`
- `shouldInjectAgentListInMessages()`
- `getPrompt()`

**Dependencies:** `../../services/analytics/growthbook`, `../../utils/auth`, `../../utils/embeddedTools`, `../../utils/envUtils`, `../../utils/teammate`, `../../utils/teammateContext`, `../FileReadTool/prompt`, `../FileWriteTool/prompt`, `../GlobTool/prompt`, `../SendMessageTool/constants`

**Main flow:** Entry: `formatAgentLine()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/resumeAgent.ts` (265 lines)

**Exports:**
- `ResumeAgentResult`
- `resumeAgentBackground()`

**Dependencies:** `fs`, `../../bootstrap/state`, `../../constants/prompts`, `../../coordinator/coordinatorMode`, `../../hooks/useCanUseTool`, `../../Tool`, `../../tasks/LocalAgentTask/LocalAgentTask`, `../../tools`, `../../types/ids`, `../../utils/agentContext`

**Main flow:** Entry: `resumeAgentBackground()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AgentTool/runAgent.ts` (973 lines)

**Exports:**
- `filterIncompleteToolCalls()`

**Dependencies:** `bun:bundle`, `crypto`, `lodash-es/uniqBy`, `src/utils/debug`, `../../bootstrap/state`, `../../commands`, `../../constants/querySource`, `../../context`, `../../hooks/useCanUseTool`

**Feature gates:** `MONITOR_TOOL`, `PROMPT_CACHE_BREAK_DETECTION`, `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `filterIncompleteToolCalls()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AskUserQuestionTool/AskUserQuestionTool.tsx` (266 lines)

**Exports:**
- `_sdkInputSchema`
- `_sdkOutputSchema`
- `Question`
- `QuestionOption`
- `Output`
- `AskUserQuestionTool`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `react`, `src/bootstrap/state`, `src/components/MessageResponse`, `src/constants/figures`, `src/utils/permissions/PermissionMode`, `zod/v4`, `../../ink`, `../../Tool`

**Feature gates:** `KAIROS`, `KAIROS_CHANNELS`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/AskUserQuestionTool/prompt.ts` (44 lines)

**Exports:**
- `ASK_USER_QUESTION_TOOL_NAME`
- `ASK_USER_QUESTION_TOOL_CHIP_WIDTH`
- `DESCRIPTION`
- `PREVIEW_FEATURE_PROMPT`
- `ASK_USER_QUESTION_TOOL_PROMPT`

**Dependencies:** `../ExitPlanModeTool/constants`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BashTool/BashTool.tsx` (1144 lines)

**Exports:**
- `isSearchOrReadBashCommand()`
- `BashToolInput`
- `Out`
- `detectBlockedSleepPattern()`
- `BashTool`

**Dependencies:** `bun:bundle`, `@anthropic-ai/sdk/resources/index.mjs`, `fs/promises`, `react`, `src/hooks/useCanUseTool`, `src/state/AppState`, `zod/v4`, `../../bootstrap/state`, `../../constants/toolLimits`, `../../services/analytics/index`

**Feature gates:** `KAIROS`, `MONITOR_TOOL`

**Main flow:** Entry: `isSearchOrReadBashCommand()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BashTool/BashToolResultMessage.tsx` (191 lines)

**Exports:**
- default `BashToolResultMessage()`

**Dependencies:** `react/compiler-runtime`, `react`, `src/utils/sandbox/sandbox-ui-utils`, `../../components/design-system/KeyboardShortcutHint`, `../../components/MessageResponse`, `../../components/shell/OutputLine`, `../../components/shell/ShellTimeDisplay`, `../../ink`, `./BashTool`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BashTool/UI.tsx` (185 lines)

**Exports:**
- `BackgroundHint()`
- `renderToolUseMessage()`
- `renderToolUseProgressMessage()`
- `renderToolUseQueuedMessage()`
- `renderToolResultMessage()`
- `renderToolUseErrorMessage()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/index.mjs`, `react`, `../../components/design-system/KeyboardShortcutHint`, `../../components/FallbackToolUseErrorMessage`, `../../components/MessageResponse`, `../../components/shell/ShellProgressMessage`, `../../ink`, `../../keybindings/useKeybinding`, `../../keybindings/useShortcutDisplay`

**Main flow:** Entry: `BackgroundHint()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BashTool/bashCommandHelpers.ts` (265 lines)

**Exports:**
- `CommandIdentityCheckers`
- `checkCommandOperatorPermissions()`

**Dependencies:** `zod/v4`, `../../utils/bash/parser`, `../../utils/permissions/PermissionResult`, `../../utils/permissions/PermissionUpdateSchema`, `../../utils/permissions/permissions`, `./BashTool`, `./bashSecurity`

**Main flow:** Entry: `checkCommandOperatorPermissions()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BashTool/bashPermissions.ts` (2621 lines)

**Exports:**
- `MAX_SUBCOMMANDS_FOR_SECURITY_CHECK`
- `MAX_SUGGESTED_RULES_FOR_COMPOUND`
- `getSimpleCommandPrefix()`
- `getFirstWordPrefix()`
- `permissionRuleExtractPrefix`
- `matchWildcardPattern()`
- `bashPermissionRule`
- `stripSafeWrappers()`
- `stripWrappersFromArgv()`
- `BINARY_HIJACK_VARS`
- `stripAllLeadingEnvVars()`
- `bashToolCheckExactMatchPermission`
- `bashToolCheckPermission`
- `checkCommandAndSuggestRules()`
- `peekSpeculativeClassifierCheck()`
- `startSpeculativeClassifierCheck()`
- `consumeSpeculativeClassifierCheck()`
- `clearSpeculativeChecks()`
- `awaitClassifierAutoApproval()`
- `executeAsyncClassifierCheck()`
- `bashToolHasPermission()`
- `isNormalizedGitCommand()`
- `isNormalizedCdCommand()`
- `commandHasAnyCd()`

**Dependencies:** `bun:bundle`, `@anthropic-ai/sdk`, `zod/v4`, `../../services/analytics/growthbook`, `../../Tool`, `../../types/permissions`, `../../utils/array`, `../../utils/bash/parser`, `../../utils/bash/shellQuote`, `../../utils/cwd`

**Feature gates:** `BASH_CLASSIFIER`, `TRANSCRIPT_CLASSIFIER`, `TREE_SITTER_BASH_SHADOW`

**Main flow:** Entry: `getSimpleCommandPrefix()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BashTool/bashSecurity.ts` (2592 lines)

**Exports:**
- `stripSafeHeredocSubstitutions()`
- `hasSafeHeredocSubstitution()`
- `bashCommandIsSafe_DEPRECATED()`
- `bashCommandIsSafeAsync_DEPRECATED()`

**Dependencies:** `src/services/analytics/index`, `../../utils/bash/heredoc`, `../../utils/bash/ParsedCommand`, `../../utils/bash/treeSitterAnalysis`, `../../utils/permissions/PermissionResult`

**Main flow:** Entry: `stripSafeHeredocSubstitutions()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BashTool/commandSemantics.ts` (140 lines)

**Exports:**
- `CommandSemantic`
- `interpretCommandResult()`

**Dependencies:** `../../utils/bash/commands`

**Main flow:** Entry: `interpretCommandResult()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BashTool/commentLabel.ts` (13 lines)

**Exports:**
- `extractBashCommentLabel()`

**Dependencies:** local only

**Main flow:** Entry: `extractBashCommentLabel()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BashTool/destructiveCommandWarning.ts` (102 lines)

**Exports:**
- `getDestructiveCommandWarning()`

**Dependencies:** local only

**Main flow:** Entry: `getDestructiveCommandWarning()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BashTool/modeValidation.ts` (115 lines)

**Exports:**
- `checkPermissionMode()`
- `getAutoAllowedCommands()`

**Dependencies:** `zod/v4`, `../../Tool`, `../../utils/bash/commands`, `../../utils/permissions/PermissionResult`, `./BashTool`

**Main flow:** Entry: `checkPermissionMode()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BashTool/pathValidation.ts` (1303 lines)

**Exports:**
- `PathCommand`
- `PATH_EXTRACTORS`
- `COMMAND_OPERATION_TYPE`
- `createPathChecker()`
- `checkPathConstraints()`
- `stripWrappersFromArgv()`

**Dependencies:** `os`, `path`, `zod/v4`, `../../Tool`, `../../utils/bash/ast`, `../../utils/bash/shellQuote`, `../../utils/path`, `../../utils/permissions/filesystem`, `../../utils/permissions/PermissionResult`, `../../utils/permissions/PermissionUpdate`

**Feature gates:** `BASH_CLASSIFIER`

**Main flow:** Entry: `createPathChecker()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BashTool/prompt.ts` (369 lines)

**Exports:**
- `getDefaultTimeoutMs()`
- `getMaxTimeoutMs()`
- `getSimplePrompt()`

**Dependencies:** `bun:bundle`, `../../constants/prompts`, `../../utils/attribution`, `../../utils/embeddedTools`, `../../utils/envUtils`, `../../utils/gitSettings`, `../../utils/permissions/filesystem`, `../../utils/sandbox/sandbox-adapter`, `../../utils/slowOperations`, `../AgentTool/constants`

**Feature gates:** `MONITOR_TOOL`

**Main flow:** Entry: `getDefaultTimeoutMs()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BashTool/readOnlyValidation.ts` (1990 lines)

**Exports:**
- `isCommandSafeViaFlagParsing()`
- `checkReadOnlyConstraints()`

**Dependencies:** `zod/v4`, `../../bootstrap/state`, `../../utils/bash/shellQuote`, `../../utils/cwd`, `../../utils/git`, `../../utils/permissions/PermissionResult`, `../../utils/platform`, `../../utils/sandbox/sandbox-adapter`, `./BashTool`, `./bashPermissions`

**Main flow:** Entry: `isCommandSafeViaFlagParsing()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BashTool/sedEditParser.ts` (322 lines)

**Exports:**
- `SedEditInfo`
- `isSedInPlaceEdit()`
- `parseSedEditCommand()`
- `applySedSubstitution()`

**Dependencies:** `crypto`, `../../utils/bash/shellQuote`

**Main flow:** Entry: `isSedInPlaceEdit()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BashTool/sedValidation.ts` (684 lines)

**Exports:**
- `isLinePrintingCommand()`
- `isPrintCommand()`
- `sedCommandIsAllowedByAllowlist()`
- `hasFileArgs()`
- `extractSedExpressions()`
- `checkSedConstraints()`

**Dependencies:** `../../Tool`, `../../utils/bash/commands`, `../../utils/bash/shellQuote`, `../../utils/permissions/PermissionResult`

**Main flow:** Entry: `isLinePrintingCommand()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BashTool/shouldUseSandbox.ts` (153 lines)

**Exports:**
- `shouldUseSandbox()`

**Dependencies:** `src/services/analytics/growthbook`, `../../utils/bash/commands`, `../../utils/sandbox/sandbox-adapter`, `../../utils/settings/settings`

**Main flow:** Entry: `shouldUseSandbox()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BashTool/toolName.ts` (2 lines)

**Exports:**
- `BASH_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BashTool/utils.ts` (223 lines)

**Exports:**
- `stripEmptyLines()`
- `isImageOutput()`
- `parseDataUri()`
- `buildImageToolResult()`
- `resizeShellImageOutput()`
- `formatOutput()`
- `stdErrAppendShellResetMessage`
- `resetCwdIfOutsideProject()`
- `createContentSummary()`

**Dependencies:** `fs/promises`, `src/bootstrap/state`, `src/services/analytics/index`, `src/Tool`, `src/utils/cwd`, `src/utils/permissions/filesystem`, `src/utils/Shell`, `../../utils/envUtils`, `../../utils/imageResizer`, `../../utils/shell/outputLimits`

**Main flow:** Entry: `stripEmptyLines()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BriefTool/BriefTool.ts` (204 lines)

**Exports:**
- `Output`
- `isBriefEntitled()`
- `isBriefEnabled()`
- `BriefTool`

**Dependencies:** `bun:bundle`, `zod/v4`, `../../bootstrap/state`, `../../services/analytics/growthbook`, `../../services/analytics/index`, `../../Tool`, `../../utils/envUtils`, `../../utils/lazySchema`, `../../utils/stringUtils`

**Feature gates:** `KAIROS`, `KAIROS_BRIEF`

**Main flow:** Entry: `isBriefEntitled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BriefTool/UI.tsx` (101 lines)

**Exports:**
- `renderToolUseMessage()`
- `renderToolResultMessage()`
- `AttachmentList()`

**Dependencies:** `react/compiler-runtime`, `figures`, `react`, `../../components/Markdown`, `../../constants/figures`, `../../ink`, `../../types/message`, `../../utils/file`, `../../utils/format`, `../../utils/formatBriefTimestamp`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BriefTool/attachments.ts` (110 lines)

**Exports:**
- `ResolvedAttachment`
- `validateAttachmentPaths()`
- `resolveAttachments()`

**Dependencies:** `bun:bundle`, `fs/promises`, `../../Tool`, `../../utils/cwd`, `../../utils/envUtils`, `../../utils/errors`, `../../utils/imagePaste`, `../../utils/path`

**Feature gates:** `BRIDGE_MODE`

**Main flow:** Entry: `validateAttachmentPaths()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BriefTool/prompt.ts` (22 lines)

**Exports:**
- `BRIEF_TOOL_NAME`
- `LEGACY_BRIEF_TOOL_NAME`
- `DESCRIPTION`
- `BRIEF_TOOL_PROMPT`
- `BRIEF_PROACTIVE_SECTION`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/BriefTool/upload.ts` (174 lines)

**Exports:**
- `BriefUploadContext`
- `uploadBriefAttachment()`

**Dependencies:** `bun:bundle`, `axios`, `crypto`, `fs/promises`, `path`, `zod/v4`, `../../constants/oauth`, `../../utils/debug`, `../../utils/lazySchema`, `../../utils/slowOperations`

**Feature gates:** `BRIDGE_MODE`

**Main flow:** Entry: `uploadBriefAttachment()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ConfigTool/ConfigTool.ts` (467 lines)

**Exports:**
- `Input`
- `Output`
- `ConfigTool`

**Dependencies:** `bun:bundle`, `zod/v4`, `../../Tool`, `../../utils/errors`, `../../utils/lazySchema`, `../../utils/log`, `../../utils/slowOperations`, `./constants`, `./prompt`

**Feature gates:** `VOICE_MODE`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ConfigTool/UI.tsx` (38 lines)

**Exports:**
- `renderToolUseMessage()`
- `renderToolResultMessage()`
- `renderToolUseRejectedMessage()`

**Dependencies:** `react`, `../../components/MessageResponse`, `../../ink`, `../../utils/slowOperations`, `./ConfigTool`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ConfigTool/constants.ts` (1 lines)

**Exports:**
- `CONFIG_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ConfigTool/prompt.ts` (93 lines)

**Exports:**
- `DESCRIPTION`
- `generatePrompt()`

**Dependencies:** `bun:bundle`, `../../utils/model/modelOptions`, `../../voice/voiceModeEnabled`

**Feature gates:** `VOICE_MODE`

**Main flow:** Entry: `generatePrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ConfigTool/supportedSettings.ts` (211 lines)

**Exports:**
- `SUPPORTED_SETTINGS`
- `isSupported()`
- `getConfig()`
- `getAllKeys()`
- `getOptionsForSetting()`
- `getPath()`

**Dependencies:** `bun:bundle`, `../../utils/config`, `../../utils/model/modelOptions`, `../../utils/model/validateModel`, `../../utils/theme`

**Feature gates:** `AUTO_THEME`, `BRIDGE_MODE`, `KAIROS`, `KAIROS_PUSH_NOTIFICATION`, `TRANSCRIPT_CLASSIFIER`, `VOICE_MODE`

**Main flow:** Entry: `isSupported()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/EnterPlanModeTool/EnterPlanModeTool.ts` (126 lines)

**Exports:**
- `Output`
- `EnterPlanModeTool`

**Dependencies:** `bun:bundle`, `zod/v4`, `../../Tool`, `../../utils/lazySchema`, `../../utils/permissions/PermissionUpdate`, `../../utils/permissions/permissionSetup`, `../../utils/planModeV2`, `./constants`, `./prompt`

**Feature gates:** `KAIROS`, `KAIROS_CHANNELS`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/EnterPlanModeTool/UI.tsx` (33 lines)

**Exports:**
- `renderToolUseMessage()`
- `renderToolResultMessage()`
- `renderToolUseRejectedMessage()`

**Dependencies:** `react`, `src/constants/figures`, `src/utils/permissions/PermissionMode`, `../../ink`, `../../Tool`, `../../types/message`, `../../utils/theme`, `./EnterPlanModeTool`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/EnterPlanModeTool/constants.ts` (1 lines)

**Exports:**
- `ENTER_PLAN_MODE_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/EnterPlanModeTool/prompt.ts` (170 lines)

**Exports:**
- `getEnterPlanModeToolPrompt()`

**Dependencies:** `../../utils/planModeV2`, `../AskUserQuestionTool/prompt`

**Main flow:** Entry: `getEnterPlanModeToolPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/EnterWorktreeTool/EnterWorktreeTool.ts` (127 lines)

**Exports:**
- `Output`
- `EnterWorktreeTool`

**Dependencies:** `zod/v4`, `../../bootstrap/state`, `../../constants/systemPromptSections`, `../../services/analytics/index`, `../../Tool`, `../../utils/claudemd`, `../../utils/cwd`, `../../utils/git`, `../../utils/lazySchema`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/EnterWorktreeTool/UI.tsx` (20 lines)

**Exports:**
- `renderToolUseMessage()`
- `renderToolResultMessage()`

**Dependencies:** `react`, `../../ink`, `../../Tool`, `../../types/message`, `../../utils/theme`, `./EnterWorktreeTool`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/EnterWorktreeTool/constants.ts` (1 lines)

**Exports:**
- `ENTER_WORKTREE_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/EnterWorktreeTool/prompt.ts` (30 lines)

**Exports:**
- `getEnterWorktreeToolPrompt()`

**Dependencies:** local only

**Main flow:** Entry: `getEnterWorktreeToolPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ExitPlanModeTool/ExitPlanModeV2Tool.ts` (493 lines)

**Exports:**
- `AllowedPrompt`
- `_sdkInputSchema`
- `outputSchema`
- `Output`
- `ExitPlanModeV2Tool`

**Dependencies:** `bun:bundle`, `fs/promises`, `zod/v4`, `../../services/analytics/index`, `../../services/analytics/metadata`, `../../utils/agentId`, `../../utils/agentSwarmsEnabled`, `../../utils/debug`, `../../utils/lazySchema`, `../../utils/log`

**Feature gates:** `KAIROS`, `KAIROS_CHANNELS`, `TRANSCRIPT_CLASSIFIER`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ExitPlanModeTool/UI.tsx` (82 lines)

**Exports:**
- `renderToolUseMessage()`
- `renderToolResultMessage()`
- `renderToolUseRejectedMessage()`

**Dependencies:** `react`, `src/components/Markdown`, `src/components/MessageResponse`, `src/components/messages/UserToolResultMessage/RejectedPlanMessage`, `src/constants/figures`, `src/utils/permissions/PermissionMode`, `../../ink`, `../../Tool`, `../../types/message`, `../../utils/file`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ExitPlanModeTool/constants.ts` (2 lines)

**Exports:**
- `EXIT_PLAN_MODE_TOOL_NAME`
- `EXIT_PLAN_MODE_V2_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ExitPlanModeTool/prompt.ts` (29 lines)

**Exports:**
- `EXIT_PLAN_MODE_V2_TOOL_PROMPT`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ExitWorktreeTool/ExitWorktreeTool.ts` (329 lines)

**Exports:**
- `Output`
- `ExitWorktreeTool`

**Dependencies:** `zod/v4`, `../../constants/systemPromptSections`, `../../services/analytics/index`, `../../Tool`, `../../utils/array`, `../../utils/claudemd`, `../../utils/execFileNoThrow`, `../../utils/hooks/hooksConfigSnapshot`, `../../utils/lazySchema`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ExitWorktreeTool/UI.tsx` (25 lines)

**Exports:**
- `renderToolUseMessage()`
- `renderToolResultMessage()`

**Dependencies:** `react`, `../../ink`, `../../Tool`, `../../types/message`, `../../utils/theme`, `./ExitWorktreeTool`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ExitWorktreeTool/constants.ts` (1 lines)

**Exports:**
- `EXIT_WORKTREE_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ExitWorktreeTool/prompt.ts` (32 lines)

**Exports:**
- `getExitWorktreeToolPrompt()`

**Dependencies:** local only

**Main flow:** Entry: `getExitWorktreeToolPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/FileEditTool/FileEditTool.ts` (625 lines)

**Exports:**
- `FileEditTool`

**Dependencies:** `path`, `src/services/analytics/index`, `../../services/analytics/growthbook`, `../../services/diagnosticTracking`, `../../services/lsp/LSPDiagnosticRegistry`, `../../services/lsp/manager`, `../../services/mcp/vscodeSdkMcp`, `../../services/teamMemorySync/teamMemSecretGuard`, `../../Tool`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/FileEditTool/UI.tsx` (289 lines)

**Exports:**
- `userFacingName()`
- `getToolUseSummary()`
- `renderToolUseMessage()`
- `renderToolResultMessage()`
- `renderToolUseRejectedMessage()`
- `renderToolUseErrorMessage()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/index.mjs`, `diff`, `react`, `src/components/FileEditToolUseRejectedMessage`, `src/components/MessageResponse`, `src/utils/messages`, `../../components/FallbackToolUseErrorMessage`, `../../components/FileEditToolUpdatedMessage`

**Main flow:** Entry: `userFacingName()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/FileEditTool/constants.ts` (11 lines)

**Exports:**
- `FILE_EDIT_TOOL_NAME`
- `CLAUDE_FOLDER_PERMISSION_PATTERN`
- `GLOBAL_CLAUDE_FOLDER_PERMISSION_PATTERN`
- `FILE_UNEXPECTEDLY_MODIFIED_ERROR`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/FileEditTool/prompt.ts` (28 lines)

**Exports:**
- `getEditToolDescription()`

**Dependencies:** `../../utils/file`, `../FileReadTool/prompt`

**Main flow:** Entry: `getEditToolDescription()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/FileEditTool/types.ts` (85 lines)

**Exports:**
- `FileEditInput`
- `EditInput`
- `FileEdit`
- `hunkSchema`
- `gitDiffSchema`
- `FileEditOutput`

**Dependencies:** `zod/v4`, `../../utils/lazySchema`, `../../utils/semanticBoolean`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/FileEditTool/utils.ts` (775 lines)

**Exports:**
- `LEFT_SINGLE_CURLY_QUOTE`
- `RIGHT_SINGLE_CURLY_QUOTE`
- `LEFT_DOUBLE_CURLY_QUOTE`
- `RIGHT_DOUBLE_CURLY_QUOTE`
- `normalizeQuotes()`
- `stripTrailingWhitespace()`
- `findActualString()`
- `preserveQuoteStyle()`
- `applyEditToFile()`
- `getPatchForEdit()`
- `getPatchForEdits()`
- `getSnippetForTwoFileDiff()`
- `getSnippetForPatch()`
- `getSnippet()`
- `getEditsForPatch()`
- `normalizeFileEditInput()`
- `areFileEditsEquivalent()`
- `areFileEditsInputsEquivalent()`

**Dependencies:** `diff`, `src/utils/log`, `src/utils/path`, `src/utils/stringUtils`, `../../utils/errors`, `./types`

**Main flow:** Entry: `normalizeQuotes()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/FileReadTool/FileReadTool.ts` (1183 lines)

**Exports:**
- `registerFileReadListener()`
- `MaxFileReadTokenExceededError`
- `Input`
- `Output`
- `FileReadTool`
- `CYBER_RISK_MITIGATION_REMINDER`
- `readImageWithTokenBudget()`

**Dependencies:** `@anthropic-ai/sdk/resources/index.mjs`, `fs/promises`, `path`, `zod/v4`, `../../constants/files`, `../../memdir/memoryAge`, `../../services/analytics/growthbook`, `../../services/analytics/index`, `../../Tool`

**Main flow:** Entry: `registerFileReadListener()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/FileReadTool/UI.tsx` (185 lines)

**Exports:**
- `renderToolUseMessage()`
- `renderToolUseTag()`
- `renderToolResultMessage()`
- `renderToolUseErrorMessage()`
- `userFacingName()`
- `getToolUseSummary()`

**Dependencies:** `@anthropic-ai/sdk/resources/index.mjs`, `react`, `src/utils/messages`, `../../components/FallbackToolUseErrorMessage`, `../../components/FilePathLink`, `../../components/MessageResponse`, `../../ink`, `../../utils/file`, `../../utils/format`, `../../utils/plans`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/FileReadTool/imageProcessor.ts` (94 lines)

**Exports:**
- `SharpInstance`
- `SharpFunction`
- `getImageProcessor()`
- `getImageCreator()`

**Dependencies:** `buffer`, `../../utils/bundledMode`

**Main flow:** Entry: `getImageProcessor()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/FileReadTool/limits.ts` (92 lines)

**Exports:**
- `DEFAULT_MAX_OUTPUT_TOKENS`
- `FileReadingLimits`
- `getDefaultFileReadingLimits`

**Dependencies:** `lodash-es/memoize`, `src/services/analytics/growthbook`, `src/utils/file`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/FileReadTool/prompt.ts` (49 lines)

**Exports:**
- `FILE_READ_TOOL_NAME`
- `FILE_UNCHANGED_STUB`
- `MAX_LINES_TO_READ`
- `DESCRIPTION`
- `LINE_FORMAT_INSTRUCTION`
- `OFFSET_INSTRUCTION_DEFAULT`
- `OFFSET_INSTRUCTION_TARGETED`
- `renderPromptTemplate()`

**Dependencies:** `../../utils/pdfUtils`, `../BashTool/toolName`

**Main flow:** Entry: `renderPromptTemplate()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/FileWriteTool/FileWriteTool.ts` (434 lines)

**Exports:**
- `Output`
- `FileWriteToolInput`
- `FileWriteTool`

**Dependencies:** `path`, `src/services/analytics/index`, `zod/v4`, `../../services/analytics/growthbook`, `../../services/diagnosticTracking`, `../../services/lsp/LSPDiagnosticRegistry`, `../../services/lsp/manager`, `../../services/mcp/vscodeSdkMcp`, `../../services/teamMemorySync/teamMemSecretGuard`, `../../Tool`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/FileWriteTool/UI.tsx` (405 lines)

**Exports:**
- `countLines()`
- `userFacingName()`
- `isResultTruncated()`
- `getToolUseSummary()`
- `renderToolUseMessage()`
- `renderToolUseRejectedMessage()`
- `renderToolUseErrorMessage()`
- `renderToolResultMessage()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/index.mjs`, `diff`, `path`, `react`, `src/components/MessageResponse`, `src/utils/messages`, `../../components/CtrlOToExpand`, `../../components/FallbackToolUseErrorMessage`

**Main flow:** Entry: `countLines()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/FileWriteTool/prompt.ts` (18 lines)

**Exports:**
- `FILE_WRITE_TOOL_NAME`
- `DESCRIPTION`
- `getWriteToolDescription()`

**Dependencies:** `../FileReadTool/prompt`

**Main flow:** Entry: `getWriteToolDescription()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/GlobTool/GlobTool.ts` (198 lines)

**Exports:**
- `Output`
- `GlobTool`

**Dependencies:** `zod/v4`, `../../Tool`, `../../utils/cwd`, `../../utils/errors`, `../../utils/fsOperations`, `../../utils/glob`, `../../utils/lazySchema`, `../../utils/path`, `../../utils/permissions/filesystem`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/GlobTool/UI.tsx` (63 lines)

**Exports:**
- `userFacingName()`
- `renderToolUseMessage()`
- `renderToolUseErrorMessage()`
- `renderToolResultMessage`
- `getToolUseSummary()`

**Dependencies:** `@anthropic-ai/sdk/resources/index.mjs`, `react`, `src/components/MessageResponse`, `src/utils/messages`, `../../components/FallbackToolUseErrorMessage`, `../../constants/toolLimits`, `../../ink`, `../../utils/file`, `../../utils/format`, `../GrepTool/GrepTool`

**Main flow:** Entry: `userFacingName()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/GlobTool/prompt.ts` (7 lines)

**Exports:**
- `GLOB_TOOL_NAME`
- `DESCRIPTION`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/GrepTool/GrepTool.ts` (577 lines)

**Exports:**
- `GrepTool`

**Dependencies:** `zod/v4`, `../../Tool`, `../../utils/cwd`, `../../utils/errors`, `../../utils/fsOperations`, `../../utils/lazySchema`, `../../utils/path`, `../../utils/permissions/PermissionResult`, `../../utils/permissions/shellRuleMatching`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/GrepTool/UI.tsx` (201 lines)

**Exports:**
- `renderToolUseMessage()`
- `renderToolUseErrorMessage()`
- `renderToolResultMessage()`
- `getToolUseSummary()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/index.mjs`, `react`, `../../components/CtrlOToExpand`, `../../components/FallbackToolUseErrorMessage`, `../../components/MessageResponse`, `../../constants/toolLimits`, `../../ink`, `../../Tool`, `../../types/message`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/GrepTool/prompt.ts` (18 lines)

**Exports:**
- `GREP_TOOL_NAME`
- `getDescription()`

**Dependencies:** `../AgentTool/constants`, `../BashTool/toolName`

**Main flow:** Entry: `getDescription()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/LSPTool/LSPTool.ts` (860 lines)

**Exports:**
- `Output`
- `Input`
- `LSPTool`

**Dependencies:** `fs/promises`, `path`, `url`, `zod/v4`, `../../Tool`, `../../utils/array`, `../../utils/cwd`, `../../utils/debug`, `../../utils/errors`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/LSPTool/UI.tsx` (228 lines)

**Exports:**
- `userFacingName()`
- `renderToolUseMessage()`
- `renderToolUseErrorMessage()`
- `renderToolResultMessage()`

**Dependencies:** `react/compiler-runtime`, `@anthropic-ai/sdk/resources/index.mjs`, `react`, `../../components/CtrlOToExpand`, `../../components/FallbackToolUseErrorMessage`, `../../components/MessageResponse`, `../../ink`, `../../utils/file`, `../../utils/messages`, `./LSPTool`

**Main flow:** Entry: `userFacingName()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/LSPTool/formatters.ts` (592 lines)

**Exports:**
- `formatGoToDefinitionResult()`
- `formatFindReferencesResult()`
- `formatHoverResult()`
- `formatDocumentSymbolResult()`
- `formatWorkspaceSymbolResult()`
- `formatPrepareCallHierarchyResult()`
- `formatIncomingCallsResult()`
- `formatOutgoingCallsResult()`

**Dependencies:** `path`, `../../utils/debug`, `../../utils/errors`, `../../utils/stringUtils`

**Main flow:** Entry: `formatGoToDefinitionResult()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/LSPTool/prompt.ts` (21 lines)

**Exports:**
- `LSP_TOOL_NAME`
- `DESCRIPTION`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/LSPTool/schemas.ts` (215 lines)

**Exports:**
- `lspToolInputSchema`
- `LSPToolInput`
- `isValidLSPOperation()`

**Dependencies:** `zod/v4`, `../../utils/lazySchema`

**Main flow:** Entry: `isValidLSPOperation()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/LSPTool/symbolContext.ts` (90 lines)

**Exports:**
- `getSymbolAtPosition()`

**Dependencies:** `../../utils/debug`, `../../utils/format`, `../../utils/fsOperations`, `../../utils/path`

**Main flow:** Entry: `getSymbolAtPosition()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ListMcpResourcesTool/ListMcpResourcesTool.ts` (123 lines)

**Exports:**
- `Output`
- `ListMcpResourcesTool`

**Dependencies:** `zod/v4`, `../../Tool`, `../../utils/errors`, `../../utils/lazySchema`, `../../utils/log`, `../../utils/slowOperations`, `../../utils/terminal`, `./prompt`, `./UI`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ListMcpResourcesTool/UI.tsx` (29 lines)

**Exports:**
- `renderToolUseMessage()`
- `renderToolResultMessage()`

**Dependencies:** `react`, `../../components/MessageResponse`, `../../components/shell/OutputLine`, `../../ink`, `../../Tool`, `../../types/message`, `../../utils/slowOperations`, `./ListMcpResourcesTool`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ListMcpResourcesTool/prompt.ts` (20 lines)

**Exports:**
- `LIST_MCP_RESOURCES_TOOL_NAME`
- `DESCRIPTION`
- `PROMPT`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/MCPTool/MCPTool.ts` (77 lines)

**Exports:**
- `inputSchema`
- `outputSchema`
- `Output`
- `MCPTool`

**Dependencies:** `zod/v4`, `../../Tool`, `../../utils/lazySchema`, `../../utils/permissions/PermissionResult`, `../../utils/terminal`, `./prompt`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/MCPTool/UI.tsx` (403 lines)

**Exports:**
- `renderToolUseMessage()`
- `renderToolUseProgressMessage()`
- `renderToolResultMessage()`
- `tryFlattenJson()`
- `tryUnwrapTextPayload()`
- `trySlackSendCompact()`

**Dependencies:** `react/compiler-runtime`, `bun:bundle`, `figures`, `react`, `zod/v4`, `../../components/design-system/ProgressBar`, `../../components/MessageResponse`, `../../components/shell/OutputLine`, `../../ink/stringWidth`, `../../ink`

**Feature gates:** `MCP_RICH_OUTPUT`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/MCPTool/classifyForCollapse.ts` (604 lines)

**Exports:**
- `classifyMcpToolForCollapse()`

**Dependencies:** local only

**Main flow:** Entry: `classifyMcpToolForCollapse()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/MCPTool/prompt.ts` (3 lines)

**Exports:**
- `PROMPT`
- `DESCRIPTION`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/McpAuthTool/McpAuthTool.ts` (215 lines)

**Exports:**
- `McpAuthOutput`
- `createMcpAuthTool()`

**Dependencies:** `lodash-es/reject`, `zod/v4`, `../../services/mcp/auth`, `../../Tool`, `../../utils/errors`, `../../utils/lazySchema`, `../../utils/log`, `../../utils/permissions/PermissionResult`

**Main flow:** Entry: `createMcpAuthTool()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/NotebookEditTool/NotebookEditTool.ts` (490 lines)

**Exports:**
- `inputSchema`
- `outputSchema`
- `Output`
- `NotebookEditTool`

**Dependencies:** `bun:bundle`, `path`, `zod/v4`, `../../Tool`, `../../types/notebook`, `../../utils/cwd`, `../../utils/errors`, `../../utils/file`, `../../utils/fileRead`, `../../utils/json`

**Feature gates:** `TRANSCRIPT_CLASSIFIER`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/NotebookEditTool/UI.tsx` (93 lines)

**Exports:**
- `getToolUseSummary()`
- `renderToolUseMessage()`
- `renderToolUseRejectedMessage()`
- `renderToolUseErrorMessage()`
- `renderToolResultMessage()`

**Dependencies:** `@anthropic-ai/sdk/resources/index.mjs`, `react`, `src/types/message`, `src/utils/messages`, `src/utils/theme`, `zod/v4`, `../../components/FallbackToolUseErrorMessage`, `../../components/FilePathLink`, `../../components/HighlightedCode`, `../../components/MessageResponse`

**Main flow:** Entry: `getToolUseSummary()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/NotebookEditTool/constants.ts` (2 lines)

**Exports:**
- `NOTEBOOK_EDIT_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/NotebookEditTool/prompt.ts` (3 lines)

**Exports:**
- `DESCRIPTION`
- `PROMPT`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/PowerShellTool/PowerShellTool.tsx` (1001 lines)

**Exports:**
- `detectBlockedSleepPattern()`
- `PowerShellToolInput`
- `Out`
- `PowerShellTool`

**Dependencies:** `bun:bundle`, `@anthropic-ai/sdk/resources/index.mjs`, `fs/promises`, `react`, `src/hooks/useCanUseTool`, `src/state/AppState`, `zod/v4`, `../../bootstrap/state`, `../../constants/toolLimits`, `../../services/analytics/index`

**Feature gates:** `KAIROS`, `MONITOR_TOOL`

**Main flow:** Entry: `detectBlockedSleepPattern()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/PowerShellTool/UI.tsx` (131 lines)

**Exports:**
- `renderToolUseMessage()`
- `renderToolUseProgressMessage()`
- `renderToolUseQueuedMessage()`
- `renderToolResultMessage()`
- `renderToolUseErrorMessage()`

**Dependencies:** `@anthropic-ai/sdk/resources/index.mjs`, `react`, `../../components/design-system/KeyboardShortcutHint`, `../../components/FallbackToolUseErrorMessage`, `../../components/MessageResponse`, `../../components/shell/OutputLine`, `../../components/shell/ShellProgressMessage`, `../../components/shell/ShellTimeDisplay`, `../../ink`, `../../Tool`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/PowerShellTool/clmTypes.ts` (211 lines)

**Exports:**
- `CLM_ALLOWED_TYPES`
- `normalizeTypeName()`
- `isClmAllowedType()`

**Dependencies:** local only

**Main flow:** Entry: `normalizeTypeName()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/PowerShellTool/commandSemantics.ts` (142 lines)

**Exports:**
- `CommandSemantic`
- `interpretCommandResult()`

**Dependencies:** local only

**Main flow:** Entry: `interpretCommandResult()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/PowerShellTool/commonParameters.ts` (30 lines)

**Exports:**
- `COMMON_SWITCHES`
- `COMMON_VALUE_PARAMS`
- `COMMON_PARAMETERS`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/PowerShellTool/destructiveCommandWarning.ts` (109 lines)

**Exports:**
- `getDestructiveCommandWarning()`

**Dependencies:** local only

**Main flow:** Entry: `getDestructiveCommandWarning()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/PowerShellTool/gitSafety.ts` (176 lines)

**Exports:**
- `isGitInternalPathPS()`
- `isDotGitPathPS()`

**Dependencies:** `path`, `../../utils/cwd`, `../../utils/powershell/parser`

**Main flow:** Entry: `isGitInternalPathPS()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/PowerShellTool/modeValidation.ts` (404 lines)

**Exports:**
- `isSymlinkCreatingCommand()`
- `checkPermissionMode()`

**Dependencies:** `../../Tool`, `../../utils/permissions/PermissionResult`, `../../utils/powershell/parser`

**Main flow:** Entry: `isSymlinkCreatingCommand()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/PowerShellTool/pathValidation.ts` (2049 lines)

**Exports:**
- `isDangerousRemovalRawPath()`
- `dangerousRemovalDeny()`
- `checkPathConstraints()`

**Dependencies:** `os`, `path`, `../../Tool`, `../../types/permissions`, `../../utils/cwd`, `../../utils/path`, `../../utils/permissions/PermissionResult`, `../../utils/permissions/PermissionUpdate`, `../../utils/permissions/PermissionUpdateSchema`, `../../utils/platform`

**Main flow:** Entry: `isDangerousRemovalRawPath()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/PowerShellTool/powershellPermissions.ts` (1648 lines)

**Exports:**
- `powershellPermissionRule()`
- `powershellToolCheckExactMatchPermission()`
- `powershellToolCheckPermission()`
- `powershellToolHasPermission()`

**Dependencies:** `path`, `../../Tool`, `../../utils/cwd`, `../../utils/git`, `../../utils/permissions/PermissionRule`, `../../utils/permissions/PermissionUpdateSchema`, `../../utils/shell/readOnlyCommandValidation`, `./gitSafety`, `./powershellSecurity`

**Main flow:** Entry: `powershellPermissionRule()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/PowerShellTool/powershellSecurity.ts` (1090 lines)

**Exports:**
- `powershellCommandIsSafe()`

**Dependencies:** `./clmTypes`

**Main flow:** Entry: `powershellCommandIsSafe()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/PowerShellTool/prompt.ts` (145 lines)

**Exports:**
- `getDefaultTimeoutMs()`
- `getMaxTimeoutMs()`
- `getPrompt()`

**Dependencies:** `../../utils/envUtils`, `../../utils/shell/outputLimits`, `../FileEditTool/constants`, `../FileReadTool/prompt`, `../FileWriteTool/prompt`, `../GlobTool/prompt`, `../GrepTool/prompt`, `./toolName`

**Main flow:** Entry: `getDefaultTimeoutMs()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/PowerShellTool/readOnlyValidation.ts` (1823 lines)

**Exports:**
- `argLeaksValue()`
- `CMDLET_ALLOWLIST`
- `resolveToCanonical()`
- `isCwdChangingCmdlet()`
- `isSafeOutputCommand()`
- `isAllowlistedPipelineTail()`
- `isProvablySafeStatement()`
- `hasSyncSecurityConcerns()`
- `isReadOnlyCommand()`
- `isAllowlistedCommand()`

**Dependencies:** `../../utils/platform`, `../../utils/shell/readOnlyCommandValidation`, `./commonParameters`

**Main flow:** Entry: `argLeaksValue()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/PowerShellTool/toolName.ts` (2 lines)

**Exports:**
- `POWERSHELL_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/REPLTool/constants.ts` (46 lines)

**Exports:**
- `REPL_TOOL_NAME`
- `isReplModeEnabled()`
- `REPL_ONLY_TOOLS`

**Dependencies:** `../../utils/envUtils`, `../AgentTool/constants`, `../BashTool/toolName`, `../FileEditTool/constants`, `../FileReadTool/prompt`, `../FileWriteTool/prompt`, `../GlobTool/prompt`, `../GrepTool/prompt`, `../NotebookEditTool/constants`

**Main flow:** Entry: `isReplModeEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/REPLTool/primitiveTools.ts` (39 lines)

**Exports:**
- `getReplPrimitiveTools()`

**Dependencies:** `../../Tool`, `../AgentTool/AgentTool`, `../BashTool/BashTool`, `../FileEditTool/FileEditTool`, `../FileReadTool/FileReadTool`, `../FileWriteTool/FileWriteTool`, `../GlobTool/GlobTool`, `../GrepTool/GrepTool`, `../NotebookEditTool/NotebookEditTool`

**Main flow:** Entry: `getReplPrimitiveTools()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ReadMcpResourceTool/ReadMcpResourceTool.ts` (158 lines)

**Exports:**
- `inputSchema`
- `outputSchema`
- `Output`
- `ReadMcpResourceTool`

**Dependencies:** `zod/v4`, `../../services/mcp/client`, `../../Tool`, `../../utils/lazySchema`, `../../utils/slowOperations`, `../../utils/terminal`, `./prompt`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ReadMcpResourceTool/UI.tsx` (37 lines)

**Exports:**
- `renderToolUseMessage()`
- `userFacingName()`
- `renderToolResultMessage()`

**Dependencies:** `react`, `zod/v4`, `../../components/MessageResponse`, `../../components/shell/OutputLine`, `../../ink`, `../../Tool`, `../../types/message`, `../../utils/slowOperations`, `./ReadMcpResourceTool`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ReadMcpResourceTool/prompt.ts` (16 lines)

**Exports:**
- `DESCRIPTION`
- `PROMPT`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/RemoteTriggerTool/RemoteTriggerTool.ts` (161 lines)

**Exports:**
- `Input`
- `Output`
- `RemoteTriggerTool`

**Dependencies:** `axios`, `zod/v4`, `../../constants/oauth`, `../../services/analytics/growthbook`, `../../services/oauth/client`, `../../services/policyLimits/index`, `../../Tool`, `../../utils/lazySchema`, `../../utils/slowOperations`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/RemoteTriggerTool/UI.tsx` (17 lines)

**Exports:**
- `renderToolUseMessage()`
- `renderToolResultMessage()`

**Dependencies:** `react`, `../../components/MessageResponse`, `../../ink`, `../../utils/stringUtils`, `./RemoteTriggerTool`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/RemoteTriggerTool/prompt.ts` (15 lines)

**Exports:**
- `REMOTE_TRIGGER_TOOL_NAME`
- `DESCRIPTION`
- `PROMPT`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ScheduleCronTool/CronCreateTool.ts` (157 lines)

**Exports:**
- `CreateOutput`
- `CronCreateTool`

**Dependencies:** `zod/v4`, `../../bootstrap/state`, `../../Tool`, `../../utils/cron`, `../../utils/lazySchema`, `../../utils/semanticBoolean`, `../../utils/teammateContext`, `./UI`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ScheduleCronTool/CronDeleteTool.ts` (95 lines)

**Exports:**
- `DeleteOutput`
- `CronDeleteTool`

**Dependencies:** `zod/v4`, `../../Tool`, `../../utils/lazySchema`, `../../utils/teammateContext`, `./UI`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ScheduleCronTool/CronListTool.ts` (97 lines)

**Exports:**
- `ListOutput`
- `CronListTool`

**Dependencies:** `zod/v4`, `../../Tool`, `../../utils/cron`, `../../utils/cronTasks`, `../../utils/format`, `../../utils/lazySchema`, `../../utils/teammateContext`, `./UI`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ScheduleCronTool/UI.tsx` (60 lines)

**Exports:**
- `renderCreateToolUseMessage()`
- `renderCreateResultMessage()`
- `renderDeleteToolUseMessage()`
- `renderDeleteResultMessage()`
- `renderListToolUseMessage()`
- `renderListResultMessage()`

**Dependencies:** `react`, `../../components/MessageResponse`, `../../ink`, `../../utils/format`, `./CronCreateTool`, `./CronDeleteTool`, `./CronListTool`

**Main flow:** Entry: `renderCreateToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ScheduleCronTool/prompt.ts` (135 lines)

**Exports:**
- `DEFAULT_MAX_AGE_DAYS`
- `isKairosCronEnabled()`
- `isDurableCronEnabled()`
- `CRON_CREATE_TOOL_NAME`
- `CRON_DELETE_TOOL_NAME`
- `CRON_LIST_TOOL_NAME`
- `buildCronCreateDescription()`
- `buildCronCreatePrompt()`
- `CRON_DELETE_DESCRIPTION`
- `buildCronDeletePrompt()`
- `CRON_LIST_DESCRIPTION`
- `buildCronListPrompt()`

**Dependencies:** `bun:bundle`, `../../services/analytics/growthbook`, `../../utils/cronTasks`, `../../utils/envUtils`

**Feature gates:** `AGENT_TRIGGERS`, `KAIROS`

**Main flow:** Entry: `isKairosCronEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/SendMessageTool/SendMessageTool.ts` (917 lines)

**Exports:**
- `Input`
- `MessageRouting`
- `MessageOutput`
- `BroadcastOutput`
- `RequestOutput`
- `ResponseOutput`
- `SendMessageToolOutput`
- `SendMessageTool`

**Dependencies:** `bun:bundle`, `zod/v4`, `../../bootstrap/state`, `../../bridge/replBridgeHandle`, `../../Tool`, `../../tasks/InProcessTeammateTask/InProcessTeammateTask`, `../../tasks/LocalMainSessionTask`, `../../types/ids`, `../../utils/agentId`

**Feature gates:** `UDS_INBOX`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/SendMessageTool/UI.tsx` (31 lines)

**Exports:**
- `renderToolUseMessage()`
- `renderToolResultMessage()`

**Dependencies:** `react`, `../../components/MessageResponse`, `../../ink`, `../../utils/slowOperations`, `./SendMessageTool`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/SendMessageTool/constants.ts` (1 lines)

**Exports:**
- `SEND_MESSAGE_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/SendMessageTool/prompt.ts` (49 lines)

**Exports:**
- `DESCRIPTION`
- `getPrompt()`

**Dependencies:** `bun:bundle`

**Feature gates:** `UDS_INBOX`

**Main flow:** Entry: `getPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/SkillTool/SkillTool.ts` (1108 lines)

**Exports:**
- `inputSchema`
- `outputSchema`
- `Output`
- `SkillTool`

**Dependencies:** `bun:bundle`, `@anthropic-ai/sdk/resources/index.mjs`, `lodash-es/uniqBy`, `path`, `src/bootstrap/state`, `src/Tool`, `src/types/command`, `src/utils/debug`, `src/utils/permissions/PermissionResult`, `src/utils/permissions/permissions`

**Feature gates:** `EXPERIMENTAL_SKILL_SEARCH`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/SkillTool/UI.tsx` (128 lines)

**Exports:**
- `renderToolResultMessage()`
- `renderToolUseMessage()`
- `renderToolUseProgressMessage()`
- `renderToolUseRejectedMessage()`
- `renderToolUseErrorMessage()`

**Dependencies:** `@anthropic-ai/sdk/resources/index.mjs`, `react`, `src/components/CtrlOToExpand`, `src/components/FallbackToolUseErrorMessage`, `src/components/FallbackToolUseRejectedMessage`, `zod/v4`, `../../commands`, `../../components/design-system/Byline`, `../../components/Message`, `../../components/MessageResponse`

**Main flow:** Entry: `renderToolResultMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/SkillTool/constants.ts` (1 lines)

**Exports:**
- `SKILL_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/SkillTool/prompt.ts` (241 lines)

**Exports:**
- `SKILL_BUDGET_CONTEXT_PERCENT`
- `CHARS_PER_TOKEN`
- `DEFAULT_CHAR_BUDGET`
- `MAX_LISTING_DESC_CHARS`
- `getCharBudget()`
- `formatCommandsWithinBudget()`
- `getPrompt`
- `getSkillToolInfo()`
- `getLimitedSkillToolCommands()`
- `clearPromptCache()`
- `getSkillInfo()`

**Dependencies:** `lodash-es`, `src/commands`, `../../constants/xml`, `../../ink/stringWidth`, `../../utils/array`, `../../utils/debug`, `../../utils/errors`, `../../utils/format`, `../../utils/log`

**Main flow:** Entry: `getCharBudget()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/SleepTool/prompt.ts` (17 lines)

**Exports:**
- `SLEEP_TOOL_NAME`
- `DESCRIPTION`
- `SLEEP_TOOL_PROMPT`

**Dependencies:** `../../constants/xml`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/SyntheticOutputTool/SyntheticOutputTool.ts` (163 lines)

**Exports:**
- `Output`
- `SYNTHETIC_OUTPUT_TOOL_NAME`
- `isSyntheticOutputToolEnabled()`
- `SyntheticOutputTool`
- `createSyntheticOutputTool()`

**Dependencies:** `ajv`, `zod/v4`, `../../Tool`, `../../utils/errors`, `../../utils/lazySchema`, `../../utils/permissions/PermissionResult`, `../../utils/slowOperations`

**Main flow:** Entry: `isSyntheticOutputToolEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TaskCreateTool/TaskCreateTool.ts` (138 lines)

**Exports:**
- `Output`
- `TaskCreateTool`

**Dependencies:** `zod/v4`, `../../Tool`, `../../utils/lazySchema`, `../../utils/teammate`, `./constants`, `./prompt`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TaskCreateTool/constants.ts` (1 lines)

**Exports:**
- `TASK_CREATE_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TaskCreateTool/prompt.ts` (56 lines)

**Exports:**
- `DESCRIPTION`
- `getPrompt()`

**Dependencies:** `../../utils/agentSwarmsEnabled`

**Main flow:** Entry: `getPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TaskGetTool/TaskGetTool.ts` (128 lines)

**Exports:**
- `Output`
- `TaskGetTool`

**Dependencies:** `zod/v4`, `../../Tool`, `../../utils/lazySchema`, `./constants`, `./prompt`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TaskGetTool/constants.ts` (1 lines)

**Exports:**
- `TASK_GET_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TaskGetTool/prompt.ts` (24 lines)

**Exports:**
- `DESCRIPTION`
- `PROMPT`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TaskListTool/TaskListTool.ts` (116 lines)

**Exports:**
- `Output`
- `TaskListTool`

**Dependencies:** `zod/v4`, `../../Tool`, `../../utils/lazySchema`, `./constants`, `./prompt`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TaskListTool/constants.ts` (1 lines)

**Exports:**
- `TASK_LIST_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TaskListTool/prompt.ts` (49 lines)

**Exports:**
- `DESCRIPTION`
- `getPrompt()`

**Dependencies:** `../../utils/agentSwarmsEnabled`

**Main flow:** Entry: `getPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TaskOutputTool/TaskOutputTool.tsx` (584 lines)

**Exports:**
- `TaskOutputTool`

**Dependencies:** `react/compiler-runtime`, `react`, `zod/v4`, `../../components/FallbackToolUseErrorMessage`, `../../components/FallbackToolUseRejectedMessage`, `../../components/MessageResponse`, `../../ink`, `../../keybindings/useShortcutDisplay`, `../../Task`, `../../Tool`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TaskOutputTool/constants.ts` (1 lines)

**Exports:**
- `TASK_OUTPUT_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TaskStopTool/TaskStopTool.ts` (131 lines)

**Exports:**
- `Output`
- `TaskStopTool`

**Dependencies:** `zod/v4`, `../../Task`, `../../Tool`, `../../tasks/stopTask`, `../../utils/lazySchema`, `../../utils/slowOperations`, `./prompt`, `./UI`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TaskStopTool/UI.tsx` (41 lines)

**Exports:**
- `renderToolUseMessage()`
- `renderToolResultMessage()`

**Dependencies:** `react`, `../../components/MessageResponse`, `../../ink/stringWidth`, `../../ink`, `../../utils/format`, `./TaskStopTool`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TaskStopTool/prompt.ts` (8 lines)

**Exports:**
- `TASK_STOP_TOOL_NAME`
- `DESCRIPTION`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TaskUpdateTool/TaskUpdateTool.ts` (406 lines)

**Exports:**
- `Output`
- `TaskUpdateTool`

**Dependencies:** `bun:bundle`, `zod/v4`, `../../services/analytics/growthbook`, `../../Tool`, `../../utils/agentSwarmsEnabled`, `../../utils/lazySchema`, `../../utils/teammateMailbox`, `../AgentTool/constants`, `./constants`, `./prompt`

**Feature gates:** `VERIFICATION_AGENT`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TaskUpdateTool/constants.ts` (1 lines)

**Exports:**
- `TASK_UPDATE_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TaskUpdateTool/prompt.ts` (77 lines)

**Exports:**
- `DESCRIPTION`
- `PROMPT`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TeamCreateTool/TeamCreateTool.ts` (240 lines)

**Exports:**
- `Output`
- `Input`
- `TeamCreateTool`

**Dependencies:** `zod/v4`, `../../bootstrap/state`, `../../services/analytics/index`, `../../services/analytics/metadata`, `../../Tool`, `../../utils/agentId`, `../../utils/agentSwarmsEnabled`, `../../utils/cwd`, `../../utils/lazySchema`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TeamCreateTool/UI.tsx` (6 lines)

**Exports:**
- `renderToolUseMessage()`

**Dependencies:** `react`, `./TeamCreateTool`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TeamCreateTool/constants.ts` (1 lines)

**Exports:**
- `TEAM_CREATE_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TeamCreateTool/prompt.ts` (113 lines)

**Exports:**
- `getPrompt()`

**Dependencies:** local only

**Main flow:** Entry: `getPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TeamDeleteTool/TeamDeleteTool.ts` (139 lines)

**Exports:**
- `Output`
- `Input`
- `TeamDeleteTool`

**Dependencies:** `zod/v4`, `../../services/analytics/index`, `../../services/analytics/metadata`, `../../Tool`, `../../utils/agentSwarmsEnabled`, `../../utils/lazySchema`, `../../utils/slowOperations`, `../../utils/swarm/constants`, `../../utils/swarm/teammateLayoutManager`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TeamDeleteTool/UI.tsx` (20 lines)

**Exports:**
- `renderToolUseMessage()`
- `renderToolResultMessage()`

**Dependencies:** `react`, `../../utils/slowOperations`, `./TeamDeleteTool`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TeamDeleteTool/constants.ts` (1 lines)

**Exports:**
- `TEAM_DELETE_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TeamDeleteTool/prompt.ts` (16 lines)

**Exports:**
- `getPrompt()`

**Dependencies:** local only

**Main flow:** Entry: `getPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TodoWriteTool/TodoWriteTool.ts` (115 lines)

**Exports:**
- `Output`
- `TodoWriteTool`

**Dependencies:** `bun:bundle`, `zod/v4`, `../../bootstrap/state`, `../../services/analytics/growthbook`, `../../Tool`, `../../utils/lazySchema`, `../../utils/tasks`, `../../utils/todo/types`, `../AgentTool/constants`, `./constants`

**Feature gates:** `VERIFICATION_AGENT`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TodoWriteTool/constants.ts` (1 lines)

**Exports:**
- `TODO_WRITE_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/TodoWriteTool/prompt.ts` (184 lines)

**Exports:**
- `PROMPT`
- `DESCRIPTION`

**Dependencies:** `../FileEditTool/constants`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ToolSearchTool/ToolSearchTool.ts` (471 lines)

**Exports:**
- `inputSchema`
- `outputSchema`
- `Output`
- `clearToolSearchDescriptionCache()`
- `ToolSearchTool`

**Dependencies:** `@anthropic-ai/sdk/resources/index.mjs`, `lodash-es/memoize`, `zod/v4`, `../../utils/debug`, `../../utils/lazySchema`, `../../utils/stringUtils`, `../../utils/toolSearch`, `./prompt`

**Main flow:** Entry: `clearToolSearchDescriptionCache()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ToolSearchTool/constants.ts` (1 lines)

**Exports:**
- `TOOL_SEARCH_TOOL_NAME`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/ToolSearchTool/prompt.ts` (121 lines)

**Exports:**
- `isDeferredTool()`
- `formatDeferredToolLine()`
- `getPrompt()`

**Dependencies:** `bun:bundle`, `../../bootstrap/state`, `../../services/analytics/growthbook`, `../../Tool`, `../AgentTool/constants`, `./constants`

**Feature gates:** `FORK_SUBAGENT`, `KAIROS`, `KAIROS_BRIEF`

**Main flow:** Entry: `isDeferredTool()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/WebFetchTool/UI.tsx` (72 lines)

**Exports:**
- `renderToolUseMessage()`
- `renderToolUseProgressMessage()`
- `renderToolResultMessage()`
- `getToolUseSummary()`

**Dependencies:** `react`, `../../components/MessageResponse`, `../../constants/toolLimits`, `../../ink`, `../../Tool`, `../../types/message`, `../../utils/format`, `./WebFetchTool`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/WebFetchTool/WebFetchTool.ts` (318 lines)

**Exports:**
- `Output`
- `WebFetchTool`

**Dependencies:** `zod/v4`, `../../Tool`, `../../types/permissions`, `../../utils/format`, `../../utils/lazySchema`, `../../utils/permissions/PermissionResult`, `../../utils/permissions/permissions`, `./preapproved`, `./prompt`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/WebFetchTool/preapproved.ts` (166 lines)

**Exports:**
- `PREAPPROVED_HOSTS`
- `isPreapprovedHost()`

**Dependencies:** local only

**Main flow:** Entry: `isPreapprovedHost()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/WebFetchTool/prompt.ts` (46 lines)

**Exports:**
- `WEB_FETCH_TOOL_NAME`
- `DESCRIPTION`
- `makeSecondaryModelPrompt()`

**Dependencies:** local only

**Main flow:** Entry: `makeSecondaryModelPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/WebFetchTool/utils.ts` (530 lines)

**Exports:**
- `clearWebFetchCache()`
- `MAX_MARKDOWN_LENGTH`
- `isPreapprovedUrl()`
- `validateURL()`
- `checkDomainBlocklist()`
- `isPermittedRedirect()`
- `getWithPermittedRedirects()`
- `FetchedContent`
- `getURLMarkdownContent()`
- `applyPromptToMarkdown()`

**Dependencies:** `axios`, `lru-cache`, `../../services/api/claude`, `../../utils/errors`, `../../utils/http`, `../../utils/log`, `../../utils/settings/settings`, `../../utils/systemPromptType`, `./preapproved`, `./prompt`

**Main flow:** Entry: `clearWebFetchCache()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/WebSearchTool/UI.tsx` (101 lines)

**Exports:**
- `renderToolUseMessage()`
- `renderToolUseProgressMessage()`
- `renderToolResultMessage()`
- `getToolUseSummary()`

**Dependencies:** `react`, `../../components/MessageResponse`, `../../constants/toolLimits`, `../../ink`, `../../types/message`, `../../utils/format`, `./WebSearchTool`

**Main flow:** Entry: `renderToolUseMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/WebSearchTool/WebSearchTool.ts` (435 lines)

**Exports:**
- `SearchResult`
- `Output`
- `WebSearchTool`

**Dependencies:** `src/utils/model/providers`, `src/utils/permissions/PermissionResult`, `zod/v4`, `../../services/analytics/growthbook`, `../../services/api/claude`, `../../Tool`, `../../utils/lazySchema`, `../../utils/log`, `../../utils/messages`, `../../utils/model/model`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/WebSearchTool/prompt.ts` (34 lines)

**Exports:**
- `WEB_SEARCH_TOOL_NAME`
- `getWebSearchPrompt()`

**Dependencies:** `src/constants/common`

**Main flow:** Entry: `getWebSearchPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/shared/gitOperationTracking.ts` (277 lines)

**Exports:**
- `CommitKind`
- `BranchAction`
- `PrAction`
- `parseGitCommitId()`
- `detectGitOperation()`
- `trackGitOperations()`

**Dependencies:** `../../bootstrap/state`

**Main flow:** Entry: `parseGitCommitId()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/shared/spawnMultiAgent.ts` (1093 lines)

**Exports:**
- `resolveTeammateModel()`
- `SpawnOutput`
- `SpawnTeammateConfig`
- `generateUniqueTeammateName()`
- `spawnTeammate()`

**Dependencies:** `react`, `../../state/AppState`, `../../Task`, `../../Tool`, `../../tasks/InProcessTeammateTask/types`, `../../utils/agentId`, `../../utils/bash/shellQuote`, `../../utils/bundledMode`, `../../utils/config`, `../../utils/cwd`

**Main flow:** Entry: `resolveTeammateModel()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/testing/TestingPermissionTool.tsx` (74 lines)

**Exports:**
- `TestingPermissionTool`

**Dependencies:** `zod/v4`, `../../Tool`, `../../utils/lazySchema`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `tools/utils.ts` (40 lines)

**Exports:**
- `tagMessagesWithToolUseID()`
- `getToolUseIDFromParentMessage()`

**Dependencies:** local only

**Main flow:** Entry: `tagMessagesWithToolUseID()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `types/command.ts` (216 lines)

**Exports:**
- `LocalCommandResult`
- `PromptCommand`
- `LocalCommandCall`
- `LocalCommandModule`
- `LocalJSXCommandContext`
- `ResumeEntrypoint`
- `CommandResultDisplay`
- `LocalJSXCommandOnDone`
- `LocalJSXCommandCall`
- `LocalJSXCommandModule`
- `CommandAvailability`
- `CommandBase`
- `Command`
- `getCommandName()`
- `isCommandEnabled()`

**Dependencies:** `@anthropic-ai/sdk/resources/index.mjs`, `crypto`, `../hooks/useCanUseTool`, `../services/compact/compact`, `../services/mcp/types`, `../Tool`, `../utils/effort`, `../utils/ide`, `../utils/settings/constants`, `../utils/settings/types`

**Main flow:** Entry: `getCommandName()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `types/hooks.ts` (290 lines)

**Exports:**
- `isHookEvent()`
- `promptRequestSchema`
- `PromptRequest`
- `PromptResponse`
- `syncHookResponseSchema`
- `hookJSONOutputSchema`
- `isSyncHookJSONOutput()`
- `isAsyncHookJSONOutput()`
- `HookCallbackContext`
- `HookCallback`
- `HookCallbackMatcher`
- `HookProgress`
- `HookBlockingError`
- `PermissionRequestResult`
- `HookResult`
- `AggregatedHookResult`

**Dependencies:** `zod/v4`, `../utils/lazySchema`, `src/types/message`, `src/utils/permissions/PermissionResult`, `src/utils/permissions/PermissionRule`, `src/utils/permissions/PermissionUpdateSchema`, `../state/AppState`, `../utils/commitAttribution`

**Main flow:** Entry: `isHookEvent()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `types/ids.ts` (44 lines)

**Exports:**
- `SessionId`
- `AgentId`
- `asSessionId()`
- `asAgentId()`
- `toAgentId()`

**Dependencies:** local only

**Main flow:** Entry: `asSessionId()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `types/logs.ts` (330 lines)

**Exports:**
- `SerializedMessage`
- `LogOption`
- `SummaryMessage`
- `CustomTitleMessage`
- `AiTitleMessage`
- `LastPromptMessage`
- `TaskSummaryMessage`
- `TagMessage`
- `AgentNameMessage`
- `AgentColorMessage`
- `AgentSettingMessage`
- `PRLinkMessage`
- `ModeEntry`
- `PersistedWorktreeSession`
- `WorktreeStateEntry`
- `ContentReplacementEntry`
- `FileHistorySnapshotMessage`
- `FileAttributionState`
- `AttributionSnapshotMessage`
- `TranscriptMessage`
- `SpeculationAcceptMessage`
- `ContextCollapseCommitEntry`
- `ContextCollapseSnapshotEntry`
- `Entry`
- `sortLogs()`

**Dependencies:** `crypto`, `src/utils/fileHistory`, `src/utils/toolResultStorage`, `./ids`, `./message`, `./messageQueueTypes`

**Main flow:** Entry: `sortLogs()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `types/permissions.ts` (441 lines)

**Exports:**
- `EXTERNAL_PERMISSION_MODES`
- `ExternalPermissionMode`
- `InternalPermissionMode`
- `PermissionMode`
- `INTERNAL_PERMISSION_MODES`
- `PERMISSION_MODES`
- `PermissionBehavior`
- `PermissionRuleSource`
- `PermissionRuleValue`
- `PermissionRule`
- `PermissionUpdateDestination`
- `PermissionUpdate`
- `WorkingDirectorySource`
- `AdditionalWorkingDirectory`
- `PermissionCommandMetadata`
- `PermissionMetadata`
- `PermissionAllowDecision`
- `PendingClassifierCheck`
- `PermissionAskDecision`
- `PermissionDenyDecision`
- `PermissionDecision`
- `PermissionResult`
- `PermissionDecisionReason`
- `ClassifierResult`
- `ClassifierBehavior`
- ... +6 more

**Dependencies:** `bun:bundle`, `@anthropic-ai/sdk/resources/messages.mjs`

**Feature gates:** `TRANSCRIPT_CLASSIFIER`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `types/plugin.ts` (363 lines)

**Exports:**
- `BuiltinPluginDefinition`
- `PluginRepository`
- `PluginConfig`
- `LoadedPlugin`
- `PluginComponent`
- `PluginError`
- `PluginLoadResult`
- `getPluginErrorMessage()`

**Dependencies:** `../services/lsp/types`, `../services/mcp/types`, `../skills/bundledSkills`, `../utils/settings/types`

**Main flow:** Entry: `getPluginErrorMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `types/textInputTypes.ts` (387 lines)

**Exports:**
- `InlineGhostText`
- `BaseTextInputProps`
- `VimTextInputProps`
- `VimMode`
- `BaseInputState`
- `TextInputState`
- `VimInputState`
- `PromptInputMode`
- `EditablePromptInputMode`
- `QueuePriority`
- `QueuedCommand`
- `isValidImagePaste()`
- `getImagePasteIds()`
- `OrphanedPermission`

**Dependencies:** `@anthropic-ai/sdk/resources/messages.mjs`, `crypto`, `react`, `../entrypoints/agentSdkTypes`, `../ink`, `../utils/config`, `../utils/imageResizer`, `../utils/textHighlighting`, `./ids`, `./message`

**Main flow:** Entry: `isValidImagePaste()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/autoRunIssue.tsx` (122 lines)

**Exports:**
- `AutoRunIssueNotification()`
- `AutoRunIssueReason`
- `shouldAutoRunIssue()`
- `getAutoRunCommand()`
- `getAutoRunIssueReasonText()`

**Dependencies:** `react/compiler-runtime`, `react`, `../components/design-system/KeyboardShortcutHint`, `../ink`, `../keybindings/useKeybinding`

**Main flow:** Entry: `AutoRunIssueNotification()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/background/remote/preconditions.ts` (235 lines)

**Exports:**
- `checkNeedsClaudeAiLogin()`
- `checkIsGitClean()`
- `checkHasRemoteEnvironment()`
- `checkIsInGitRepo()`
- `checkHasGitRemote()`
- `checkGithubAppInstalled()`
- `checkGithubTokenSynced()`
- `checkRepoForRemoteAccess()`

**Dependencies:** `axios`, `src/constants/oauth`, `src/services/oauth/client`, `../../../services/analytics/growthbook`, `../../cwd`, `../../debug`, `../../detectRepository`, `../../errors`, `../../git`, `../../teleport/api`

**Main flow:** Entry: `checkNeedsClaudeAiLogin()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/background/remote/remoteSession.ts` (98 lines)

**Exports:**
- `BackgroundRemoteSession`
- `BackgroundRemoteSessionPrecondition`
- `checkBackgroundRemoteSessionEligibility()`

**Dependencies:** `src/entrypoints/agentSdkTypes`, `../../../services/analytics/growthbook`, `../../../services/policyLimits/index`, `../../detectRepository`, `../../envUtils`, `../../todo/types`

**Main flow:** Entry: `checkBackgroundRemoteSessionEligibility()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/ParsedCommand.ts` (318 lines)

**Exports:**
- `OutputRedirection`
- `IParsedCommand`
- `RegexParsedCommand_DEPRECATED`
- `buildParsedCommandFromRoot()`
- `ParsedCommand`

**Dependencies:** `lodash-es/memoize`, `./parser`

**Main flow:** Entry: `buildParsedCommandFromRoot()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/ShellSnapshot.ts` (582 lines)

**Exports:**
- `createRipgrepShellIntegration()`
- `createFindGrepShellIntegration()`
- `createAndSaveSnapshot`

**Dependencies:** `child_process`, `execa`, `fs/promises`, `os`, `path`, `src/services/analytics/index`, `../cleanupRegistry`, `../cwd`, `../debug`, `../envUtils`

**Main flow:** Entry: `createRipgrepShellIntegration()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/ast.ts` (2679 lines)

**Exports:**
- `Redirect`
- `SimpleCommand`
- `ParseForSecurityResult`
- `nodeTypeId()`
- `parseForSecurity()`
- `parseForSecurityFromAst()`
- `SemanticCheckResult`
- `checkSemantics()`

**Dependencies:** `./bashParser`, `./parser`

**Main flow:** Entry: `nodeTypeId()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/bashParser.ts` (4436 lines)

**Exports:**
- `TsNode`
- `ensureParserInitialized()`
- `getParserModule()`
- `SHELL_KEYWORDS`

**Dependencies:** local only

**Main flow:** Entry: `ensureParserInitialized()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/bashPipeCommand.ts` (294 lines)

**Exports:**
- `rearrangePipeCommand()`

**Dependencies:** local only

**Main flow:** Entry: `rearrangePipeCommand()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/commands.ts` (1339 lines)

**Exports:**
- `splitCommandWithOperators()`
- `filterControlOperators()`
- `splitCommand_DEPRECATED()`
- `isHelpCommand()`
- `getCommandSubcommandPrefix`
- `clearCommandPrefixCaches()`
- `isUnsafeCompoundCommand_DEPRECATED()`
- `extractOutputRedirections()`

**Dependencies:** `crypto`, `shell-quote`, `./heredoc`, `./shellQuote`

**Main flow:** Entry: `splitCommandWithOperators()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/heredoc.ts` (733 lines)

**Exports:**
- `HeredocInfo`
- `HeredocExtractionResult`
- `extractHeredocs()`
- `restoreHeredocs()`
- `containsHeredoc()`

**Dependencies:** `crypto`

**Main flow:** Entry: `extractHeredocs()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/parser.ts` (230 lines)

**Exports:**
- `Node`
- `ParsedCommandData`
- `ensureInitialized()`
- `parseCommand()`
- `PARSE_ABORTED`
- `parseCommandRaw()`
- `extractCommandArguments()`

**Dependencies:** `bun:bundle`, `../../services/analytics/index`, `../debug`

**Feature gates:** `TREE_SITTER_BASH`, `TREE_SITTER_BASH_SHADOW`

**Main flow:** Entry: `ensureInitialized()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/prefix.ts` (204 lines)

**Exports:**
- `getCommandPrefixStatic()`
- `getCompoundCommandPrefixesStatic()`

**Dependencies:** `../shell/specPrefix`, `./commands`, `./parser`, `./registry`

**Main flow:** Entry: `getCommandPrefixStatic()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/registry.ts` (53 lines)

**Exports:**
- `CommandSpec`
- `Argument`
- `Option`
- `loadFigSpec()`
- `getCommandSpec`

**Dependencies:** `../memoize`, `./specs/index`

**Main flow:** Entry: `loadFigSpec()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/shellCompletion.ts` (259 lines)

**Exports:**
- `ShellCompletionType`
- `getShellCompletions()`

**Dependencies:** `src/components/PromptInput/PromptInputFooterSuggestions`, `../debug`, `../localInstaller`, `../Shell`

**Main flow:** Entry: `getShellCompletions()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/shellPrefix.ts` (28 lines)

**Exports:**
- `formatShellPrefixCommand()`

**Dependencies:** `./shellQuote`

**Main flow:** Entry: `formatShellPrefixCommand()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/shellQuote.ts` (304 lines)

**Exports:**
- `ShellParseResult`
- `ShellQuoteResult`
- `tryParseShellCommand()`
- `tryQuoteShellArgs()`
- `hasMalformedTokens()`
- `hasShellQuoteSingleQuoteBug()`
- `quote()`

**Dependencies:** `../log`, `../slowOperations`

**Main flow:** Entry: `tryParseShellCommand()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/shellQuoting.ts` (128 lines)

**Exports:**
- `quoteShellCommand()`
- `hasStdinRedirect()`
- `shouldAddStdinRedirect()`
- `rewriteWindowsNullRedirect()`

**Dependencies:** `./shellQuote`

**Main flow:** Entry: `quoteShellCommand()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/specs/alias.ts` (14 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../registry`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/specs/index.ts` (18 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../registry`, `./alias`, `./nohup`, `./pyright`, `./sleep`, `./srun`, `./time`, `./timeout`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/specs/nohup.ts` (13 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../registry`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/specs/pyright.ts` (91 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../registry`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/specs/sleep.ts` (13 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../registry`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/specs/srun.ts` (31 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../registry`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/specs/time.ts` (13 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../registry`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/specs/timeout.ts` (20 lines)

**Exports:**
- (none — internal module)

**Dependencies:** `../registry`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/bash/treeSitterAnalysis.ts` (506 lines)

**Exports:**
- `QuoteContext`
- `CompoundStructure`
- `DangerousPatterns`
- `TreeSitterAnalysis`
- `extractQuoteContext()`
- `extractCompoundStructure()`
- `hasActualOperatorNodes()`
- `extractDangerousPatterns()`
- `analyzeCommand()`

**Dependencies:** local only

**Main flow:** Entry: `extractQuoteContext()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/claudeInChrome/chromeNativeHost.ts` (527 lines)

**Exports:**
- `sendChromeMessage()`
- `runChromeNativeHost()`

**Dependencies:** `net`, `os`, `path`, `zod`, `../lazySchema`, `../slowOperations`, `./common`

**Main flow:** Entry: `sendChromeMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/claudeInChrome/common.ts` (540 lines)

**Exports:**
- `CLAUDE_IN_CHROME_MCP_SERVER_NAME`
- `CHROMIUM_BROWSERS`
- `BROWSER_DETECTION_ORDER`
- `getAllBrowserDataPaths()`
- `getAllNativeMessagingHostsDirs()`
- `getAllWindowsRegistryKeys()`
- `detectAvailableBrowser()`
- `isClaudeInChromeMCPServer()`
- `trackClaudeInChromeTabId()`
- `isTrackedClaudeInChromeTabId()`
- `openInChrome()`
- `getSocketDir()`
- `getSecureSocketPath()`
- `getAllSocketPaths()`

**Dependencies:** `fs`, `fs/promises`, `os`, `path`, `../../services/mcp/normalization`, `../debug`, `../errors`, `../execFileNoThrow`, `../platform`, `../which`

**Main flow:** Entry: `getAllBrowserDataPaths()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/claudeInChrome/mcpServer.ts` (293 lines)

**Exports:**
- `createChromeContext()`
- `runClaudeInChromeMcpServer()`

**Dependencies:** `@modelcontextprotocol/sdk/server/stdio`, `util`, `../../services/analytics/datadog`, `../../services/analytics/firstPartyEventLogger`, `../../services/analytics/growthbook`, `../../services/analytics/sink`, `../auth`, `../config`, `../debug`, `../envUtils`

**Main flow:** Entry: `createChromeContext()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/claudeInChrome/prompt.ts` (83 lines)

**Exports:**
- `BASE_CHROME_PROMPT`
- `CHROME_TOOL_SEARCH_INSTRUCTIONS`
- `getChromeSystemPrompt()`
- `CLAUDE_IN_CHROME_SKILL_HINT`
- `CLAUDE_IN_CHROME_SKILL_HINT_WITH_WEBBROWSER`

**Dependencies:** local only

**Main flow:** Entry: `getChromeSystemPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/claudeInChrome/setup.ts` (400 lines)

**Exports:**
- `shouldEnableClaudeInChrome()`
- `shouldAutoEnableClaudeInChrome()`
- `setupClaudeInChrome()`
- `installChromeNativeHostManifest()`
- `isChromeExtensionInstalled()`

**Dependencies:** `@ant/claude-for-chrome-mcp`, `fs/promises`, `os`, `path`, `url`, `../../services/analytics/growthbook`, `../../services/mcp/types`, `../bundledMode`, `../config`, `../debug`

**Main flow:** Entry: `shouldEnableClaudeInChrome()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/claudeInChrome/setupPortable.ts` (233 lines)

**Exports:**
- `CHROME_EXTENSION_URL`
- `ChromiumBrowser`
- `BrowserPath`
- `getAllBrowserDataPathsPortable()`
- `detectExtensionInstallationPortable()`
- `isChromeExtensionInstalledPortable()`
- `isChromeExtensionInstalled()`

**Dependencies:** `fs/promises`, `os`, `path`, `../errors`

**Main flow:** Entry: `getAllBrowserDataPathsPortable()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/claudeInChrome/toolRendering.tsx` (262 lines)

**Exports:**
- `ChromeToolName`
- `renderChromeToolResultMessage()`
- `getClaudeInChromeMCPToolOverrides()`

**Dependencies:** `react`, `../../components/MessageResponse`, `../../ink/supports-hyperlinks`, `../../ink`, `../../tools/MCPTool/UI`, `../../utils/mcpValidation`, `../format`, `./common`

**Main flow:** Entry: `renderChromeToolResultMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/computerUse/appNames.ts` (196 lines)

**Exports:**
- `filterAppsForDescription()`

**Dependencies:** local only

**Main flow:** Entry: `filterAppsForDescription()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/computerUse/cleanup.ts` (86 lines)

**Exports:**
- `cleanupComputerUseAfterTurn()`

**Dependencies:** `../../Tool`, `../debug`, `../errors`, `../withResolvers`, `./computerUseLock`, `./escHotkey`

**Feature gates:** `CHICAGO_MCP`

**Main flow:** Entry: `cleanupComputerUseAfterTurn()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/computerUse/common.ts` (61 lines)

**Exports:**
- `COMPUTER_USE_MCP_SERVER_NAME`
- `CLI_HOST_BUNDLE_ID`
- `getTerminalBundleId()`
- `CLI_CU_CAPABILITIES`
- `isComputerUseMCPServer()`

**Dependencies:** `../../services/mcp/normalization`, `../env`

**Main flow:** Entry: `getTerminalBundleId()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/computerUse/computerUseLock.ts` (215 lines)

**Exports:**
- `AcquireResult`
- `CheckResult`
- `checkComputerUseLock()`
- `isLockHeldLocally()`
- `tryAcquireComputerUseLock()`
- `releaseComputerUseLock()`

**Dependencies:** `fs/promises`, `path`, `../../bootstrap/state`, `../../utils/cleanupRegistry`, `../../utils/debug`, `../../utils/envUtils`, `../../utils/slowOperations`, `../errors`

**Main flow:** Entry: `checkComputerUseLock()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/computerUse/drainRunLoop.ts` (79 lines)

**Exports:**
- `retainPump`
- `releasePump`
- `drainRunLoop()`

**Dependencies:** `../debug`, `../withResolvers`, `./swiftLoader`

**Main flow:** Entry: `drainRunLoop()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/computerUse/escHotkey.ts` (54 lines)

**Exports:**
- `registerEscHotkey()`
- `unregisterEscHotkey()`
- `notifyExpectedEscape()`

**Dependencies:** `../debug`, `./drainRunLoop`, `./swiftLoader`

**Main flow:** Entry: `registerEscHotkey()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/computerUse/executor.ts` (658 lines)

**Exports:**
- `createCliExecutor()`
- `unhideComputerUseApps()`

**Dependencies:** `@ant/computer-use-mcp`, `../debug`, `../errors`, `../execFileNoThrow`, `../sleep`, `./drainRunLoop`

**Main flow:** Entry: `createCliExecutor()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/computerUse/gates.ts` (72 lines)

**Exports:**
- `getChicagoEnabled()`
- `getChicagoSubGates()`
- `getChicagoCoordinateMode()`

**Dependencies:** `@ant/computer-use-mcp/types`, `../../services/analytics/growthbook`, `../auth`, `../envUtils`

**Main flow:** Entry: `getChicagoEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/computerUse/hostAdapter.ts` (69 lines)

**Exports:**
- `getComputerUseHostAdapter()`

**Dependencies:** `util`, `../debug`, `./common`, `./executor`, `./gates`, `./swiftLoader`

**Main flow:** Entry: `getComputerUseHostAdapter()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/computerUse/inputLoader.ts` (30 lines)

**Exports:**
- `requireComputerUseInput()`

**Dependencies:** local only

**Main flow:** Entry: `requireComputerUseInput()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/computerUse/mcpServer.ts` (106 lines)

**Exports:**
- `createComputerUseMcpServerForCli()`
- `runComputerUseMcpServer()`

**Dependencies:** `@modelcontextprotocol/sdk/server/stdio`, `@modelcontextprotocol/sdk/types`, `os`, `../../services/analytics/datadog`, `../../services/analytics/firstPartyEventLogger`, `../../services/analytics/sink`, `../config`, `../debug`, `./appNames`, `./gates`

**Main flow:** Entry: `createComputerUseMcpServerForCli()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/computerUse/setup.ts` (53 lines)

**Exports:**
- `setupComputerUseMCP()`

**Dependencies:** `@ant/computer-use-mcp`, `path`, `url`, `../../services/mcp/mcpStringUtils`, `../../services/mcp/types`, `../bundledMode`, `./common`, `./gates`

**Main flow:** Entry: `setupComputerUseMCP()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/computerUse/swiftLoader.ts` (23 lines)

**Exports:**
- `requireComputerUseSwift()`

**Dependencies:** `@ant/computer-use-swift`

**Main flow:** Entry: `requireComputerUseSwift()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/computerUse/toolRendering.tsx` (125 lines)

**Exports:**
- `getComputerUseMCPRenderingOverrides()`

**Dependencies:** `react`, `../../components/MessageResponse`, `../../ink`, `../format`, `../mcpValidation`

**Main flow:** Entry: `getComputerUseMCPRenderingOverrides()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/computerUse/wrapper.tsx` (336 lines)

**Exports:**
- `buildSessionContext()`
- `getComputerUseMCPToolOverrides()`

**Dependencies:** `@ant/computer-use-mcp`, `react`, `../../bootstrap/state`, `../../components/permissions/ComputerUseApproval/ComputerUseApproval`, `../../Tool`, `../debug`, `./computerUseLock`, `./escHotkey`, `./gates`, `./hostAdapter`

**Feature gates:** `CHICAGO_MCP`

**Main flow:** Entry: `buildSessionContext()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/deepLink/banner.ts` (123 lines)

**Exports:**
- `DeepLinkBannerInfo`
- `buildDeepLinkBanner()`
- `readLastFetchTime()`

**Dependencies:** `fs/promises`, `os`, `path`, `../format`, `../git/gitFilesystem`, `../git`

**Main flow:** Entry: `buildDeepLinkBanner()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/deepLink/parseDeepLink.ts` (170 lines)

**Exports:**
- `DEEP_LINK_PROTOCOL`
- `DeepLinkAction`
- `parseDeepLink()`
- `buildDeepLink()`

**Dependencies:** `../sanitization`

**Main flow:** Entry: `parseDeepLink()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/deepLink/protocolHandler.ts` (136 lines)

**Exports:**
- `handleDeepLinkUri()`
- `handleUrlSchemeLaunch()`

**Dependencies:** `os`, `../debug`, `../slowOperations`, `./banner`, `./parseDeepLink`, `./registerProtocol`, `./terminalLauncher`

**Main flow:** Entry: `handleDeepLinkUri()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/deepLink/registerProtocol.ts` (348 lines)

**Exports:**
- `MACOS_BUNDLE_ID`
- `registerProtocolHandler()`
- `isProtocolHandlerCurrent()`
- `ensureDeepLinkProtocolRegistered()`

**Dependencies:** `fs`, `os`, `path`, `src/services/analytics/growthbook`, `../debug`, `../envUtils`, `../errors`, `../execFileNoThrow`, `../settings/settings`, `../which`

**Main flow:** Entry: `registerProtocolHandler()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/deepLink/terminalLauncher.ts` (557 lines)

**Exports:**
- `TerminalInfo`
- `detectTerminal()`
- `launchInTerminal()`

**Dependencies:** `child_process`, `path`, `../config`, `../debug`, `../execFileNoThrow`, `../which`

**Main flow:** Entry: `detectTerminal()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/deepLink/terminalPreference.ts` (54 lines)

**Exports:**
- `updateDeepLinkTerminalPreference()`

**Dependencies:** `../config`, `../debug`

**Main flow:** Entry: `updateDeepLinkTerminalPreference()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/dxt/helpers.ts` (88 lines)

**Exports:**
- `validateManifest()`
- `parseAndValidateManifestFromText()`
- `parseAndValidateManifestFromBytes()`
- `generateExtensionId()`

**Dependencies:** `@anthropic-ai/mcpb`, `../errors`, `../slowOperations`

**Main flow:** Entry: `validateManifest()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/dxt/zip.ts` (226 lines)

**Exports:**
- `isPathSafe()`
- `validateZipFile()`
- `unzipFile()`
- `parseZipModes()`
- `readAndUnzipFile()`

**Dependencies:** `path`, `../debug`, `../errors`, `../fsOperations`, `../path`

**Main flow:** Entry: `isPathSafe()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/exportRenderer.tsx` (98 lines)

**Exports:**
- `streamRenderedMessages()`
- `renderMessagesToPlainText()`

**Dependencies:** `react`, `strip-ansi`, `../components/Messages`, `../keybindings/KeybindingContext`, `../keybindings/loadUserBindings`, `../keybindings/types`, `../state/AppState`, `../Tool`, `../types/message`, `./staticRender`

**Main flow:** Entry: `streamRenderedMessages()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/filePersistence/filePersistence.ts` (287 lines)

**Exports:**
- `runFilePersistence()`
- `executeFilePersistence()`
- `isFilePersistenceEnabled()`

**Dependencies:** `bun:bundle`, `path`, `../cwd`, `../errors`, `../log`, `../sessionIngressAuth`

**Feature gates:** `FILE_PERSISTENCE`

**Main flow:** Entry: `runFilePersistence()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/filePersistence/outputsScanner.ts` (126 lines)

**Exports:**
- `logDebug()`
- `getEnvironmentKind()`
- `findModifiedFiles()`

**Dependencies:** `fs/promises`, `path`, `../debug`, `../teleport/environments`, `./types`

**Main flow:** Entry: `logDebug()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/git/gitConfigParser.ts` (277 lines)

**Exports:**
- `parseGitConfigValue()`
- `parseConfigString()`

**Dependencies:** `fs/promises`, `path`

**Main flow:** Entry: `parseGitConfigValue()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/git/gitFilesystem.ts` (699 lines)

**Exports:**
- `clearResolveGitDirCache()`
- `resolveGitDir()`
- `isSafeRefName()`
- `isValidGitSha()`
- `readGitHead()`
- `resolveRef()`
- `getCommonDir()`
- `readRawSymref()`
- `getCachedBranch()`
- `getCachedHead()`
- `getCachedRemoteUrl()`
- `getCachedDefaultBranch()`
- `resetGitFileWatcher()`
- `getHeadForDir()`
- `readWorktreeHeadSha()`
- `getRemoteUrlForDir()`
- `isShallowClone()`
- `getWorktreeCountFromFs()`

**Dependencies:** `fs`, `fs/promises`, `path`, `../../bootstrap/state`, `../cleanupRegistry`, `../cwd`, `../git`, `./gitConfigParser`

**Main flow:** Entry: `clearResolveGitDirCache()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/git/gitignore.ts` (99 lines)

**Exports:**
- `isPathGitignored()`
- `getGlobalGitignorePath()`
- `addFileGlobRuleToGitignore()`

**Dependencies:** `fs/promises`, `os`, `path`, `../cwd`, `../errors`, `../execFileNoThrow`, `../git`, `../log`

**Main flow:** Entry: `isPathGitignored()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/github/ghAuthStatus.ts` (29 lines)

**Exports:**
- `GhAuthStatus`
- `getGhAuthStatus()`

**Dependencies:** `execa`, `../which`

**Main flow:** Entry: `getGhAuthStatus()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/highlightMatch.tsx` (28 lines)

**Exports:**
- `highlightMatch()`

**Dependencies:** `react`, `../ink`

**Main flow:** Entry: `highlightMatch()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/hooks/AsyncHookRegistry.ts` (309 lines)

**Exports:**
- `PendingAsyncHook`
- `registerPendingAsyncHook()`
- `getPendingAsyncHooks()`
- `checkForAsyncHookResponses()`
- `removeDeliveredAsyncHooks()`
- `finalizePendingAsyncHooks()`
- `clearAllAsyncHooks()`

**Dependencies:** `../debug`, `../ShellCommand`, `../sessionEnvironment`, `../slowOperations`, `./hookEvents`

**Main flow:** Entry: `registerPendingAsyncHook()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/hooks/apiQueryHookHelper.ts` (141 lines)

**Exports:**
- `ApiQueryHookContext`
- `ApiQueryHookConfig`
- `ApiQueryResult`
- `createApiQueryHook()`

**Dependencies:** `crypto`, `../../constants/querySource`, `../../services/api/claude`, `../../types/message`, `../../utils/abortController`, `../../utils/log`, `../errors`, `../messages`, `../systemPromptType`, `./postSamplingHooks`

**Main flow:** Entry: `createApiQueryHook()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/hooks/execAgentHook.ts` (339 lines)

**Exports:**
- `execAgentHook()`

**Dependencies:** `crypto`, `src/entrypoints/agentSdkTypes`, `../../query`, `../../services/analytics/index`, `../../services/analytics/metadata`, `../../Tool`, `../../tools/SyntheticOutputTool/SyntheticOutputTool`, `../../tools`, `../../types/ids`

**Main flow:** Entry: `execAgentHook()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/hooks/execHttpHook.ts` (242 lines)

**Exports:**
- `execHttpHook()`

**Dependencies:** `axios`, `src/entrypoints/agentSdkTypes`, `../combinedAbortSignal`, `../debug`, `../errors`, `../proxy`, `../settings/settings`, `../settings/types`, `./ssrfGuard`

**Main flow:** Entry: `execHttpHook()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/hooks/execPromptHook.ts` (211 lines)

**Exports:**
- `execPromptHook()`

**Dependencies:** `crypto`, `src/entrypoints/agentSdkTypes`, `../../services/api/claude`, `../../Tool`, `../../types/message`, `../attachments`, `../combinedAbortSignal`, `../debug`, `../errors`, `../hooks`

**Main flow:** Entry: `execPromptHook()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/hooks/fileChangedWatcher.ts` (191 lines)

**Exports:**
- `setEnvHookNotifier()`
- `initializeFileChangedWatcher()`
- `updateWatchPaths()`
- `onCwdChangedForHooks()`
- `resetFileChangedWatcherForTesting()`

**Dependencies:** `chokidar`, `path`, `../cleanupRegistry`, `../debug`, `../errors`, `../sessionEnvironment`, `./hooksConfigSnapshot`

**Main flow:** Entry: `setEnvHookNotifier()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/hooks/hookEvents.ts` (192 lines)

**Exports:**
- `HookStartedEvent`
- `HookProgressEvent`
- `HookResponseEvent`
- `HookExecutionEvent`
- `HookEventHandler`
- `registerHookEventHandler()`
- `emitHookStarted()`
- `emitHookProgress()`
- `startHookProgressInterval()`
- `emitHookResponse()`
- `setAllHookEventsEnabled()`
- `clearHookEventState()`

**Dependencies:** `src/entrypoints/sdk/coreTypes`, `../debug`

**Main flow:** Entry: `registerHookEventHandler()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/hooks/hookHelpers.ts` (83 lines)

**Exports:**
- `hookResponseSchema`
- `addArgumentsToPrompt()`
- `createStructuredOutputTool()`
- `registerStructuredOutputEnforcement()`

**Dependencies:** `zod/v4`, `../../Tool`, `../argumentSubstitution`, `../lazySchema`, `../messageQueueManager`, `../messages`, `./sessionHooks`

**Main flow:** Entry: `addArgumentsToPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/hooks/hooksConfigManager.ts` (400 lines)

**Exports:**
- `MatcherMetadata`
- `HookEventMetadata`
- `getHookEventMetadata`
- `groupHooksByEventAndMatcher()`
- `getSortedMatchersForEvent()`
- `getHooksForMatcher()`
- `getMatcherMetadata()`

**Dependencies:** `lodash-es/memoize`, `src/entrypoints/agentSdkTypes`, `../../bootstrap/state`, `../../state/AppState`

**Main flow:** Entry: `groupHooksByEventAndMatcher()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/hooks/hooksConfigSnapshot.ts` (133 lines)

**Exports:**
- `shouldAllowManagedHooksOnly()`
- `shouldDisableAllHooksIncludingManaged()`
- `captureHooksConfigSnapshot()`
- `updateHooksConfigSnapshot()`
- `getHooksConfigFromSnapshot()`
- `resetHooksConfigSnapshot()`

**Dependencies:** `../../bootstrap/state`, `../settings/pluginOnlyPolicy`, `../settings/settings`, `../settings/settingsCache`, `../settings/types`

**Main flow:** Entry: `shouldAllowManagedHooksOnly()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/hooks/hooksSettings.ts` (271 lines)

**Exports:**
- `HookSource`
- `IndividualHookConfig`
- `isHookEqual()`
- `getHookDisplayText()`
- `getAllHooks()`
- `getHooksForEvent()`
- `hookSourceDescriptionDisplayString()`
- `hookSourceHeaderDisplayString()`
- `hookSourceInlineDisplayString()`
- `sortMatchersByPriority()`

**Dependencies:** `path`, `src/entrypoints/agentSdkTypes`, `../../bootstrap/state`, `../../state/AppState`, `../settings/constants`, `../settings/types`, `../shell/shellProvider`, `./sessionHooks`

**Main flow:** Entry: `isHookEqual()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/hooks/postSamplingHooks.ts` (70 lines)

**Exports:**
- `REPLHookContext`
- `PostSamplingHook`
- `registerPostSamplingHook()`
- `clearPostSamplingHooks()`
- `executePostSamplingHooks()`

**Dependencies:** `../../constants/querySource`, `../../Tool`, `../../types/message`, `../errors`, `../log`, `../systemPromptType`

**Main flow:** Entry: `registerPostSamplingHook()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/hooks/registerFrontmatterHooks.ts` (67 lines)

**Exports:**
- `registerFrontmatterHooks()`

**Dependencies:** `src/entrypoints/agentSdkTypes`, `src/state/AppState`, `../debug`, `../settings/types`, `./sessionHooks`

**Main flow:** Entry: `registerFrontmatterHooks()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/hooks/registerSkillHooks.ts` (64 lines)

**Exports:**
- `registerSkillHooks()`

**Dependencies:** `src/entrypoints/agentSdkTypes`, `src/state/AppState`, `../debug`, `../settings/types`, `./sessionHooks`

**Main flow:** Entry: `registerSkillHooks()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/hooks/sessionHooks.ts` (447 lines)

**Exports:**
- `FunctionHookCallback`
- `FunctionHook`
- `SessionStore`
- `SessionHooksState`
- `addSessionHook()`
- `addFunctionHook()`
- `removeFunctionHook()`
- `removeSessionHook()`
- `SessionDerivedHookMatcher`
- `getSessionHooks()`
- `getSessionFunctionHooks()`
- `getSessionHookCallback()`
- `clearSessionHooks()`

**Dependencies:** `src/entrypoints/agentSdkTypes`, `src/state/AppState`, `src/types/message`, `../debug`, `../hooks`, `../settings/types`, `./hooksSettings`

**Main flow:** Entry: `addSessionHook()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/hooks/skillImprovement.ts` (267 lines)

**Exports:**
- `SkillUpdate`
- `initSkillImprovement()`
- `applySkillImprovement()`

**Dependencies:** `bun:bundle`, `../../bootstrap/state`, `../../services/analytics/growthbook`, `../../services/api/claude`, `../../Tool`, `../../types/message`, `../abortController`, `../array`, `../cwd`, `../errors`

**Feature gates:** `SKILL_IMPROVEMENT`

**Main flow:** Entry: `initSkillImprovement()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/hooks/ssrfGuard.ts` (294 lines)

**Exports:**
- `isBlockedAddress()`
- `ssrfGuardedLookup()`

**Dependencies:** `axios`, `dns`, `net`

**Main flow:** Entry: `isBlockedAddress()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/mcp/dateTimeParser.ts` (121 lines)

**Exports:**
- `DateTimeParseResult`
- `parseNaturalLanguageDateTime()`
- `looksLikeISO8601()`

**Dependencies:** `../../services/api/claude`, `../log`, `../messages`, `../systemPromptType`

**Main flow:** Entry: `parseNaturalLanguageDateTime()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/mcp/elicitationValidation.ts` (336 lines)

**Exports:**
- `ValidationResult`
- `isEnumSchema`
- `isMultiSelectEnumSchema()`
- `getMultiSelectValues()`
- `getMultiSelectLabels()`
- `getMultiSelectLabel()`
- `getEnumValues()`
- `getEnumLabels()`
- `getEnumLabel()`
- `validateElicitationInput()`
- `getFormatHint()`
- `isDateTimeSchema()`
- `validateElicitationInputAsync()`

**Dependencies:** `zod/v4`, `../slowOperations`, `../stringUtils`

**Main flow:** Entry: `isMultiSelectEnumSchema()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/memory/types.ts` (12 lines)

**Exports:**
- `MEMORY_TYPE_VALUES`
- `MemoryType`

**Dependencies:** `bun:bundle`

**Feature gates:** `TEAMMEM`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/memory/versions.ts` (8 lines)

**Exports:**
- `projectIsInGitRepo()`

**Dependencies:** `../git`

**Main flow:** Entry: `projectIsInGitRepo()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/messages/mappers.ts` (290 lines)

**Exports:**
- `toInternalMessages()`
- `toSDKCompactMetadata()`
- `fromSDKCompactMetadata()`
- `toSDKMessages()`
- `localCommandOutputToSDKAssistantMessage()`
- `toSDKRateLimitInfo()`

**Dependencies:** `@anthropic-ai/sdk/resources/beta/messages/messages.mjs`, `crypto`, `src/bootstrap/state`, `src/services/claudeAiLimits`, `src/tools/ExitPlanModeTool/constants`, `src/types/utils`, `strip-ansi`, `../messages`, `../plans`

**Main flow:** Entry: `toInternalMessages()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/messages/systemInit.ts` (96 lines)

**Exports:**
- `sdkCompatToolName()`
- `SystemInitInputs`
- `buildSystemInitMessage()`

**Dependencies:** `bun:bundle`, `crypto`, `src/bootstrap/state`, `src/constants/outputStyles`, `../auth`, `../cwd`, `../fastMode`, `../settings/settings`

**Feature gates:** `UDS_INBOX`

**Main flow:** Entry: `sdkCompatToolName()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/model/agent.ts` (157 lines)

**Exports:**
- `AGENT_MODEL_OPTIONS`
- `AgentModelAlias`
- `AgentModelOption`
- `getDefaultSubagentModel()`
- `getAgentModel()`
- `getAgentModelDisplay()`
- `getAgentModelOptions()`

**Dependencies:** `../permissions/PermissionMode`, `../stringUtils`, `./aliases`, `./bedrock`, `./providers`

**Main flow:** Entry: `getDefaultSubagentModel()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/model/aliases.ts` (25 lines)

**Exports:**
- `MODEL_ALIASES`
- `ModelAlias`
- `isModelAlias()`
- `MODEL_FAMILY_ALIASES`
- `isModelFamilyAlias()`

**Dependencies:** local only

**Main flow:** Entry: `isModelAlias()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/model/antModels.ts` (64 lines)

**Exports:**
- `AntModel`
- `AntModelSwitchCalloutConfig`
- `AntModelOverrideConfig`
- `getAntModelOverrideConfig()`
- `getAntModels()`
- `resolveAntModel()`

**Dependencies:** `src/services/analytics/growthbook`, `../effort`

**Main flow:** Entry: `getAntModelOverrideConfig()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/model/bedrock.ts` (265 lines)

**Exports:**
- `getBedrockInferenceProfiles`
- `findFirstMatch()`
- `createBedrockRuntimeClient()`
- `getInferenceProfileBackingModel`
- `isFoundationModel()`
- `extractModelIdFromArn()`
- `BedrockRegionPrefix`
- `getBedrockRegionPrefix()`
- `applyBedrockRegionPrefix()`

**Dependencies:** `lodash-es/memoize`, `../auth`, `../envUtils`, `../log`, `../proxy`

**Main flow:** Entry: `findFirstMatch()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/model/check1mAccess.ts` (72 lines)

**Exports:**
- `checkOpus1mAccess()`
- `checkSonnet1mAccess()`

**Dependencies:** `src/services/claudeAiLimits`, `../auth`, `../config`, `../context`

**Main flow:** Entry: `checkOpus1mAccess()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/model/configs.ts` (118 lines)

**Exports:**
- `ModelConfig`
- `CLAUDE_3_7_SONNET_CONFIG`
- `CLAUDE_3_5_V2_SONNET_CONFIG`
- `CLAUDE_3_5_HAIKU_CONFIG`
- `CLAUDE_HAIKU_4_5_CONFIG`
- `CLAUDE_SONNET_4_CONFIG`
- `CLAUDE_SONNET_4_5_CONFIG`
- `CLAUDE_OPUS_4_CONFIG`
- `CLAUDE_OPUS_4_1_CONFIG`
- `CLAUDE_OPUS_4_5_CONFIG`
- `CLAUDE_OPUS_4_6_CONFIG`
- `CLAUDE_SONNET_4_6_CONFIG`
- `ALL_MODEL_CONFIGS`
- `ModelKey`
- `CanonicalModelId`
- `CANONICAL_MODEL_IDS`
- `CANONICAL_ID_TO_KEY`

**Dependencies:** `./model`, `./providers`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/model/contextWindowUpgradeCheck.ts` (47 lines)

**Exports:**
- `getUpgradeMessage()`

**Dependencies:** `./check1mAccess`, `./model`

**Main flow:** Entry: `getUpgradeMessage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/model/deprecation.ts` (101 lines)

**Exports:**
- `getModelDeprecationWarning()`

**Dependencies:** `./providers`

**Main flow:** Entry: `getModelDeprecationWarning()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/model/model.ts` (618 lines)

**Exports:**
- `ModelShortName`
- `ModelName`
- `ModelSetting`
- `getSmallFastModel()`
- `isNonCustomOpusModel()`
- `getUserSpecifiedModelSetting()`
- `getMainLoopModel()`
- `getBestModel()`
- `getDefaultOpusModel()`
- `getDefaultSonnetModel()`
- `getDefaultHaikuModel()`
- `getRuntimeMainLoopModel()`
- `getDefaultMainLoopModelSetting()`
- `getDefaultMainLoopModel()`
- `firstPartyNameToCanonical()`
- `getCanonicalName()`
- `getClaudeAiUserDefaultModelDescription()`
- `renderDefaultModelSetting()`
- `getOpus46PricingSuffix()`
- `isOpus1mMergeEnabled()`
- `renderModelSetting()`
- `getPublicModelDisplayName()`
- `renderModelName()`
- `getPublicModelName()`
- `parseUserSpecifiedModel()`
- ... +5 more

**Dependencies:** `../../bootstrap/state`, `../envUtils`, `./modelStrings`, `../modelCost`, `../settings/settings`, `../permissions/PermissionMode`, `./providers`, `../../constants/figures`, `./modelAllowlist`, `./aliases`

**Main flow:** Entry: `getSmallFastModel()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/model/modelAllowlist.ts` (170 lines)

**Exports:**
- `isModelAllowed()`

**Dependencies:** `../settings/settings`, `./aliases`, `./model`, `./modelStrings`

**Main flow:** Entry: `isModelAllowed()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/model/modelCapabilities.ts` (118 lines)

**Exports:**
- `ModelCapability`
- `getModelCapability()`
- `refreshModelCapabilities()`

**Dependencies:** `fs`, `fs/promises`, `lodash-es/isEqual`, `lodash-es/memoize`, `path`, `zod/v4`, `../../constants/oauth`, `../../services/api/client`, `../auth`, `../debug`

**Main flow:** Entry: `getModelCapability()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/model/modelOptions.ts` (540 lines)

**Exports:**
- `ModelOption`
- `getDefaultOptionForUser()`
- `getSonnet46_1MOption()`
- `getOpus46_1MOption()`
- `getMaxSonnet46_1MOption()`
- `getMaxOpus46_1MOption()`
- `getModelOptions()`

**Dependencies:** `../../bootstrap/state`, `./modelStrings`, `../settings/settings`, `./check1mAccess`, `./providers`, `./modelAllowlist`, `../context`, `../config`

**Main flow:** Entry: `getDefaultOptionForUser()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/model/modelStrings.ts` (166 lines)

**Exports:**
- `ModelStrings`
- `resolveOverriddenModel()`
- `getModelStrings()`
- `ensureModelStringsInitialized()`

**Dependencies:** `../log`, `../sequential`, `../settings/settings`, `./bedrock`, `./providers`

**Main flow:** Entry: `resolveOverriddenModel()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/model/modelSupportOverrides.ts` (50 lines)

**Exports:**
- `ModelCapabilityOverride`
- `get3PModelCapabilityOverride`

**Dependencies:** `lodash-es/memoize`, `./providers`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/model/providers.ts` (40 lines)

**Exports:**
- `APIProvider`
- `getAPIProvider()`
- `getAPIProviderForStatsig()`
- `isFirstPartyAnthropicBaseUrl()`

**Dependencies:** `../../services/analytics/index`, `../envUtils`

**Main flow:** Entry: `getAPIProvider()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/model/validateModel.ts` (159 lines)

**Exports:**
- `validateModel()`

**Dependencies:** `./aliases`, `./modelAllowlist`, `./providers`, `../sideQuery`, `./modelStrings`

**Main flow:** Entry: `validateModel()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/nativeInstaller/download.ts` (523 lines)

**Exports:**
- `ARTIFACTORY_REGISTRY_URL`
- `getLatestVersionFromArtifactory()`
- `getLatestVersionFromBinaryRepo()`
- `getLatestVersion()`
- `downloadVersionFromArtifactory()`
- `downloadVersionFromBinaryRepo()`
- `downloadVersion()`
- `STALL_TIMEOUT_MS`
- `_downloadAndVerifyBinaryForTesting`

**Dependencies:** `bun:bundle`, `axios`, `crypto`, `fs/promises`, `path`, `src/services/analytics/index`, `../config`, `../debug`, `../errors`, `../execFileNoThrow`

**Feature gates:** `ALLOW_TEST_VERSIONS`

**Main flow:** Entry: `getLatestVersionFromArtifactory()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/nativeInstaller/index.ts` (18 lines)

**Exports:**
- (none — internal module)

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/nativeInstaller/installer.ts` (1708 lines)

**Exports:**
- `VERSION_RETENTION_COUNT`
- `SetupMessage`
- `getPlatform()`
- `getBinaryName()`
- `removeDirectoryIfEmpty()`
- `checkInstall()`
- `installLatest()`
- `lockCurrentVersion()`
- `cleanupOldVersions()`
- `removeInstalledSymlink()`
- `cleanupShellAliases()`
- `cleanupNpmInstallations()`

**Dependencies:** `fs`, `os`, `path`, `../autoUpdater`, `../cleanupRegistry`, `../config`, `../debug`, `../doctorDiagnostic`, `../env`, `../envDynamic`

**Main flow:** Entry: `getPlatform()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/nativeInstaller/packageManagers.ts` (336 lines)

**Exports:**
- `PackageManager`
- `getOsRelease`
- `detectMise()`
- `detectAsdf()`
- `detectHomebrew()`
- `detectWinget()`
- `detectPacman`
- `detectDeb`
- `detectRpm`
- `detectApk`
- `getPackageManager`

**Dependencies:** `fs/promises`, `lodash-es/memoize`, `../debug`, `../execFileNoThrow`, `../platform`

**Main flow:** Entry: `detectMise()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/nativeInstaller/pidLock.ts` (433 lines)

**Exports:**
- `isPidBasedLockingEnabled()`
- `VersionLockContent`
- `LockInfo`
- `isProcessRunning()`
- `readLockContent()`
- `isLockActive()`
- `tryAcquireLock()`
- `acquireProcessLifetimeLock()`
- `withLock()`
- `getAllLockInfo()`
- `cleanupStaleLocks()`

**Dependencies:** `path`, `../../services/analytics/growthbook`, `../debug`, `../envUtils`, `../errors`, `../fsOperations`, `../genericProcessUtils`, `../log`

**Main flow:** Entry: `isPidBasedLockingEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/PermissionMode.ts` (141 lines)

**Exports:**
- `permissionModeSchema`
- `externalPermissionModeSchema`
- `isExternalPermissionMode()`
- `toExternalPermissionMode()`
- `permissionModeFromString()`
- `permissionModeTitle()`
- `isDefaultMode()`
- `permissionModeShortTitle()`
- `permissionModeSymbol()`
- `getModeColor()`

**Dependencies:** `bun:bundle`, `zod/v4`, `../../constants/figures`, `../lazySchema`

**Feature gates:** `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `isExternalPermissionMode()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/PermissionPromptToolResultSchema.ts` (127 lines)

**Exports:**
- `inputSchema`
- `Input`
- `outputSchema`
- `Output`
- `permissionPromptToolResultToPermissionDecision()`

**Dependencies:** `src/Tool`, `zod/v4`, `../debug`, `../lazySchema`, `./PermissionUpdateSchema`

**Main flow:** Entry: `permissionPromptToolResultToPermissionDecision()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/PermissionResult.ts` (35 lines)

**Exports:**
- `getRuleBehaviorDescription()`

**Dependencies:** local only

**Main flow:** Entry: `getRuleBehaviorDescription()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/PermissionRule.ts` (40 lines)

**Exports:**
- `permissionBehaviorSchema`
- `permissionRuleValueSchema`

**Dependencies:** `zod/v4`, `../lazySchema`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/PermissionUpdate.ts` (389 lines)

**Exports:**
- `extractRules()`
- `hasRules()`
- `applyPermissionUpdate()`
- `applyPermissionUpdates()`
- `supportsPersistence()`
- `persistPermissionUpdate()`
- `persistPermissionUpdates()`
- `createReadRuleSuggestion()`

**Dependencies:** `path`, `../../Tool`, `../debug`, `../settings/constants`, `../slowOperations`, `./filesystem`, `./PermissionRule`, `./permissionsLoader`

**Main flow:** Entry: `extractRules()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/PermissionUpdateSchema.ts` (78 lines)

**Exports:**
- `permissionUpdateDestinationSchema`
- `permissionUpdateSchema`

**Dependencies:** `zod/v4`, `../lazySchema`, `./PermissionMode`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/autoModeState.ts` (39 lines)

**Exports:**
- `setAutoModeActive()`
- `isAutoModeActive()`
- `setAutoModeFlagCli()`
- `getAutoModeFlagCli()`
- `setAutoModeCircuitBroken()`
- `isAutoModeCircuitBroken()`
- `_resetForTesting()`

**Dependencies:** local only

**Feature gates:** `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `setAutoModeActive()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/bashClassifier.ts` (61 lines)

**Exports:**
- `PROMPT_PREFIX`
- `ClassifierResult`
- `ClassifierBehavior`
- `extractPromptDescription()`
- `createPromptRuleContent()`
- `isClassifierPermissionsEnabled()`
- `getBashPromptDenyDescriptions()`
- `getBashPromptAskDescriptions()`
- `getBashPromptAllowDescriptions()`
- `classifyBashCommand()`
- `generateGenericDescription()`

**Dependencies:** local only

**Main flow:** Entry: `extractPromptDescription()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/bypassPermissionsKillswitch.ts` (155 lines)

**Exports:**
- `checkAndDisableBypassPermissionsIfNeeded()`
- `resetBypassPermissionsCheck()`
- `useKickOffCheckAndDisableBypassPermissionsIfNeeded()`
- `checkAndDisableAutoModeIfNeeded()`
- `resetAutoModeGateCheck()`
- `useKickOffCheckAndDisableAutoModeIfNeeded()`

**Dependencies:** `bun:bundle`, `react`, `src/Tool`, `../../bootstrap/state`

**Feature gates:** `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `checkAndDisableBypassPermissionsIfNeeded()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/classifierDecision.ts` (98 lines)

**Exports:**
- `isAutoModeAllowlistedTool()`

**Dependencies:** `bun:bundle`, `../../tools/AskUserQuestionTool/prompt`, `../../tools/EnterPlanModeTool/constants`, `../../tools/ExitPlanModeTool/constants`, `../../tools/FileReadTool/prompt`, `../../tools/GlobTool/prompt`, `../../tools/GrepTool/prompt`, `../../tools/ListMcpResourcesTool/prompt`, `../../tools/LSPTool/prompt`, `../../tools/SendMessageTool/constants`

**Feature gates:** `OVERFLOW_TEST_TOOL`, `TERMINAL_PANEL`, `WORKFLOW_SCRIPTS`

**Main flow:** Entry: `isAutoModeAllowlistedTool()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/classifierShared.ts` (39 lines)

**Exports:**
- `extractToolUseBlock()`
- `parseClassifierResponse()`

**Dependencies:** `@anthropic-ai/sdk/resources/beta/messages`, `zod/v4`

**Main flow:** Entry: `extractToolUseBlock()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/dangerousPatterns.ts` (80 lines)

**Exports:**
- `CROSS_PLATFORM_CODE_EXEC`
- `DANGEROUS_BASH_PATTERNS`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/denialTracking.ts` (45 lines)

**Exports:**
- `DenialTrackingState`
- `DENIAL_LIMITS`
- `createDenialTrackingState()`
- `recordDenial()`
- `recordSuccess()`
- `shouldFallbackToPrompting()`

**Dependencies:** local only

**Main flow:** Entry: `createDenialTrackingState()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/filesystem.ts` (1777 lines)

**Exports:**
- `DANGEROUS_FILES`
- `DANGEROUS_DIRECTORIES`
- `normalizeCaseForComparison()`
- `getClaudeSkillScope()`
- `relativePath()`
- `toPosixPath()`
- `isClaudeSettingsPath()`
- `getSessionMemoryDir()`
- `getSessionMemoryPath()`
- `isScratchpadEnabled()`
- `getClaudeTempDirName()`
- `getClaudeTempDir`
- `getBundledSkillsRoot`
- `getProjectTempDir()`
- `getScratchpadDir()`
- `ensureScratchpadDir()`
- `checkPathSafetyForAutoEdit()`
- `allWorkingDirectories()`
- `getResolvedWorkingDirPaths`
- `pathInAllowedWorkingPath()`
- `pathInWorkingPath()`
- `normalizePatternsToPath()`
- `getFileReadIgnorePatterns()`
- `matchingRuleForInput()`
- `checkReadPermissionForTool()`
- ... +4 more

**Dependencies:** `bun:bundle`, `crypto`, `ignore`, `lodash-es/memoize`, `os`, `path`, `src/memdir/paths`, `src/tools/AgentTool/agentMemory`, `zod/v4`, `../../bootstrap/state`

**Feature gates:** `TEMPLATES`

**Main flow:** Entry: `normalizeCaseForComparison()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/getNextPermissionMode.ts` (101 lines)

**Exports:**
- `getNextPermissionMode()`
- `cyclePermissionMode()`

**Dependencies:** `bun:bundle`, `../../Tool`, `../debug`, `./PermissionMode`

**Feature gates:** `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `getNextPermissionMode()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/pathValidation.ts` (485 lines)

**Exports:**
- `FileOperationType`
- `PathCheckResult`
- `ResolvedPathCheckResult`
- `formatDirectoryList()`
- `getGlobBaseDirectory()`
- `expandTilde()`
- `isPathInSandboxWriteAllowlist()`
- `isPathAllowed()`
- `validateGlobPattern()`
- `isDangerousRemovalPath()`
- `validatePath()`

**Dependencies:** `lodash-es/memoize`, `os`, `path`, `../../Tool`, `../../utils/platform`, `../path`, `../sandbox/sandbox-adapter`, `../shell/readOnlyCommandValidation`, `./PermissionResult`

**Main flow:** Entry: `formatDirectoryList()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/permissionExplainer.ts` (250 lines)

**Exports:**
- `RiskLevel`
- `PermissionExplanation`
- `isPermissionExplainerEnabled()`
- `generatePermissionExplanation()`

**Dependencies:** `zod/v4`, `../../services/analytics/index`, `../../services/analytics/metadata`, `../../types/message`, `../config`, `../debug`, `../errors`, `../lazySchema`, `../log`, `../model/model`

**Main flow:** Entry: `isPermissionExplainerEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/permissionRuleParser.ts` (198 lines)

**Exports:**
- `normalizeLegacyToolName()`
- `getLegacyToolNames()`
- `escapeRuleContent()`
- `unescapeRuleContent()`
- `permissionRuleValueFromString()`
- `permissionRuleValueToString()`

**Dependencies:** `bun:bundle`, `../../tools/AgentTool/constants`, `../../tools/TaskOutputTool/constants`, `../../tools/TaskStopTool/prompt`, `./PermissionRule`

**Feature gates:** `KAIROS`, `KAIROS_BRIEF`

**Main flow:** Entry: `normalizeLegacyToolName()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/permissionSetup.ts` (1532 lines)

**Exports:**
- `isDangerousBashPermission()`
- `isDangerousPowerShellPermission()`
- `isDangerousTaskPermission()`
- `DangerousPermissionInfo`
- `findDangerousClassifierPermissions()`
- `isOverlyBroadBashAllowRule()`
- `isOverlyBroadPowerShellAllowRule()`
- `findOverlyBroadBashPermissions()`
- `findOverlyBroadPowerShellPermissions()`
- `removeDangerousPermissions()`
- `stripDangerousPermissionsForAutoMode()`
- `restoreDangerousPermissions()`
- `transitionPermissionMode()`
- `parseBaseToolsFromCLI()`
- `initialPermissionModeFromCLI()`
- `parseToolListFromCLI()`
- `initializeToolPermissionContext()`
- `AutoModeGateCheckResult`
- `AutoModeUnavailableReason`
- `getAutoModeUnavailableNotification()`
- `verifyAutoModeGateAccess()`
- `shouldDisableBypassPermissions()`
- `isAutoModeGateEnabled()`
- `getAutoModeUnavailableReason()`
- `AutoModeEnabledState`
- ... +10 more

**Dependencies:** `bun:bundle`, `path`, `../cwd`, `../envUtils`, `../settings/constants`, `./permissions`, `./permissionsLoader`

**Feature gates:** `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `isDangerousBashPermission()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/permissions.ts` (1486 lines)

**Exports:**
- `permissionRuleSourceDisplayString()`
- `getAllowRules()`
- `createPermissionRequestMessage()`
- `getDenyRules()`
- `getAskRules()`
- `toolAlwaysAllowedRule()`
- `getDenyRuleForTool()`
- `getAskRuleForTool()`
- `getDenyRuleForAgent()`
- `filterDeniedAgents()`
- `getRuleByContentsForTool()`
- `getRuleByContentsForToolName()`
- `hasPermissionsToUseTool`
- `checkRuleBasedPermissions()`
- `deletePermissionRule()`
- `applyPermissionRulesToPermissionContext()`
- `syncPermissionRulesFromDisk()`

**Dependencies:** `bun:bundle`, `@anthropic-ai/sdk`, `../../hooks/useCanUseTool`, `../../Tool`, `../../tools/AgentTool/constants`, `../../tools/BashTool/shouldUseSandbox`, `../../tools/BashTool/toolName`, `../../tools/PowerShellTool/toolName`, `../../tools/REPLTool/constants`, `../../types/message`

**Feature gates:** `BASH_CLASSIFIER`, `POWERSHELL_AUTO_MODE`, `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `permissionRuleSourceDisplayString()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/permissionsLoader.ts` (296 lines)

**Exports:**
- `shouldAllowManagedPermissionRulesOnly()`
- `shouldShowAlwaysAllowOptions()`
- `loadAllPermissionRulesFromDisk()`
- `getPermissionRulesForSource()`
- `PermissionRuleFromEditableSettings`
- `deletePermissionRuleFromSettings()`
- `addPermissionRulesToSettings()`

**Dependencies:** `../fileRead`, `../fsOperations`, `../json`, `../log`, `../settings/types`

**Main flow:** Entry: `shouldAllowManagedPermissionRulesOnly()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/shadowedRuleDetection.ts` (234 lines)

**Exports:**
- `ShadowType`
- `UnreachableRule`
- `DetectUnreachableRulesOptions`
- `isSharedSettingSource()`
- `detectUnreachableRules()`

**Dependencies:** `../../Tool`, `../../tools/BashTool/toolName`, `./PermissionRule`

**Main flow:** Entry: `isSharedSettingSource()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/shellRuleMatching.ts` (228 lines)

**Exports:**
- `ShellPermissionRule`
- `permissionRuleExtractPrefix()`
- `hasWildcards()`
- `matchWildcardPattern()`
- `parsePermissionRule()`
- `suggestionForExactCommand()`
- `suggestionForPrefix()`

**Dependencies:** `./PermissionUpdateSchema`

**Main flow:** Entry: `permissionRuleExtractPrefix()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/permissions/yoloClassifier.ts` (1495 lines)

**Exports:**
- `AutoModeRules`
- `getDefaultExternalAutoModeRules()`
- `buildDefaultExternalSystemPrompt()`
- `getAutoModeClassifierErrorDumpPath()`
- `getAutoModeClassifierTranscript()`
- `YOLO_CLASSIFIER_TOOL_NAME`
- `TranscriptEntry`
- `buildTranscriptEntries()`
- `buildTranscriptForClassifier()`
- `buildYoloSystemPrompt()`
- `classifyYoloAction()`
- `formatActionForClassifier()`

**Dependencies:** `bun:bundle`, `@anthropic-ai/sdk`, `@anthropic-ai/sdk/resources/beta/messages`, `fs/promises`, `path`, `zod/v4`, `../../services/analytics/growthbook`, `../../services/analytics/index`, `../../services/analytics/metadata`, `../../services/api/claude`

**Feature gates:** `BASH_CLASSIFIER`, `POWERSHELL_AUTO_MODE`, `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `getDefaultExternalAutoModeRules()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/addDirPluginSettings.ts` (71 lines)

**Exports:**
- `getAddDirEnabledPlugins()`
- `getAddDirExtraMarketplaces()`

**Dependencies:** `path`, `zod/v4`, `../../bootstrap/state`, `../settings/settings`

**Main flow:** Entry: `getAddDirEnabledPlugins()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/cacheUtils.ts` (196 lines)

**Exports:**
- `clearAllPluginCaches()`
- `clearAllCaches()`
- `markPluginVersionOrphaned()`
- `cleanupOrphanedPluginVersionsInBackground()`

**Dependencies:** `fs/promises`, `path`, `../../commands`, `../../constants/outputStyles`, `../../tools/AgentTool/loadAgentsDir`, `../../tools/SkillTool/prompt`, `../attachments`, `../debug`, `../errors`, `../log`

**Main flow:** Entry: `clearAllPluginCaches()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/dependencyResolver.ts` (305 lines)

**Exports:**
- `qualifyDependency()`
- `DependencyLookupResult`
- `ResolutionResult`
- `resolveDependencyClosure()`
- `verifyAndDemote()`
- `findReverseDependents()`
- `getEnabledPluginIdsForScope()`
- `formatDependencyCountSuffix()`
- `formatReverseDependentsSuffix()`

**Dependencies:** `../../types/plugin`, `../settings/constants`, `../settings/settings`, `./pluginIdentifier`, `./schemas`

**Main flow:** Entry: `qualifyDependency()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/fetchTelemetry.ts` (135 lines)

**Exports:**
- `PluginFetchSource`
- `PluginFetchOutcome`
- `logPluginFetch()`
- `classifyFetchError()`

**Dependencies:** `./officialMarketplace`

**Main flow:** Entry: `logPluginFetch()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/gitAvailability.ts` (69 lines)

**Exports:**
- `checkGitAvailable`
- `markGitUnavailable()`
- `clearGitAvailabilityCache()`

**Dependencies:** `lodash-es/memoize`, `../which`

**Main flow:** Entry: `markGitUnavailable()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/headlessPluginInstall.ts` (174 lines)

**Exports:**
- `installPluginsForHeadless()`

**Dependencies:** `../../services/analytics/index`, `../cleanupRegistry`, `../debug`, `../diagLogs`, `../fsOperations`, `../log`, `./pluginBlocklist`, `./pluginLoader`, `./reconciler`, `./zipCacheAdapters`

**Main flow:** Entry: `installPluginsForHeadless()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/hintRecommendation.ts` (164 lines)

**Exports:**
- `PluginHintRecommendation`
- `maybeRecordPluginHint()`
- `_resetHintRecommendationForTesting()`
- `resolvePluginHint()`
- `markHintPluginShown()`
- `disableHintRecommendations()`

**Dependencies:** `../../services/analytics/growthbook`, `../config`, `../debug`, `./installedPluginsManager`, `./marketplaceManager`, `./pluginPolicy`

**Main flow:** Entry: `maybeRecordPluginHint()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/installCounts.ts` (292 lines)

**Exports:**
- `getInstallCounts()`
- `formatInstallCount()`

**Dependencies:** `axios`, `crypto`, `fs/promises`, `path`, `../debug`, `../errors`, `../fsOperations`, `../log`, `../slowOperations`, `./fetchTelemetry`

**Main flow:** Entry: `getInstallCounts()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/installedPluginsManager.ts` (1268 lines)

**Exports:**
- `PersistableScope`
- `getInstalledPluginsFilePath()`
- `getInstalledPluginsV2FilePath()`
- `clearInstalledPluginsCache()`
- `migrateToSinglePluginFile()`
- `resetMigrationState()`
- `loadInstalledPluginsV2()`
- `addPluginInstallation()`
- `removePluginInstallation()`
- `getInMemoryInstalledPlugins()`
- `loadInstalledPluginsFromDisk()`
- `updateInstallationPathOnDisk()`
- `hasPendingUpdates()`
- `getPendingUpdateCount()`
- `getPendingUpdatesDetails()`
- `resetInMemoryState()`
- `initializeVersionedPlugins()`
- `removeAllPluginsForMarketplace()`
- `isInstallationRelevantToCurrentProject()`
- `isPluginInstalled()`
- `isPluginGloballyInstalled()`
- `addInstalledPlugin()`
- `removeInstalledPlugin()`
- `deletePluginCache()`
- `migrateFromEnabledPlugins()`

**Dependencies:** `path`, `../debug`, `../errors`, `../fsOperations`, `../log`, `./pluginDirectories`, `../../bootstrap/state`, `../cwd`, `../git/gitFilesystem`, `../settings/constants`

**Main flow:** Entry: `getInstalledPluginsFilePath()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/loadPluginAgents.ts` (348 lines)

**Exports:**
- `loadPluginAgents`
- `clearPluginAgentCache()`

**Dependencies:** `lodash-es/memoize`, `path`, `../../memdir/paths`, `../../tools/AgentTool/agentColorManager`, `../../tools/AgentTool/loadAgentsDir`, `../../tools/FileEditTool/constants`, `../../tools/FileReadTool/prompt`, `../../tools/FileWriteTool/prompt`, `../../types/plugin`, `../debug`

**Main flow:** Entry: `clearPluginAgentCache()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/loadPluginCommands.ts` (946 lines)

**Exports:**
- `getPluginCommands`
- `clearPluginCommandCache()`
- `getPluginSkills`
- `clearPluginSkillsCache()`

**Dependencies:** `lodash-es/memoize`, `path`, `../../bootstrap/state`, `../../types/command`, `../../types/plugin`, `../debug`, `../effort`, `../envUtils`, `../errors`, `../fsOperations`

**Main flow:** Entry: `clearPluginCommandCache()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/loadPluginHooks.ts` (287 lines)

**Exports:**
- `loadPluginHooks`
- `clearPluginHookCache()`
- `pruneRemovedPluginHooks()`
- `resetHotReloadState()`
- `getPluginAffectingSettingsSnapshot()`
- `setupPluginHookHotReload()`

**Dependencies:** `lodash-es/memoize`, `src/entrypoints/agentSdkTypes`, `../../types/plugin`, `../debug`, `../settings/changeDetector`, `../settings/types`, `../slowOperations`, `./pluginLoader`

**Main flow:** Entry: `clearPluginHookCache()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/loadPluginOutputStyles.ts` (178 lines)

**Exports:**
- `loadPluginOutputStyles`
- `clearPluginOutputStyleCache()`

**Dependencies:** `lodash-es/memoize`, `path`, `../../constants/outputStyles`, `../../types/plugin`, `../debug`, `../fsOperations`, `../markdownConfigLoader`, `./pluginLoader`, `./walkPluginMarkdown`

**Main flow:** Entry: `clearPluginOutputStyleCache()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/lspPluginIntegration.ts` (387 lines)

**Exports:**
- `loadPluginLspServers()`
- `resolvePluginLspEnvironment()`
- `addPluginScopeToLspServers()`
- `getPluginLspServers()`
- `extractLspServersFromPlugins()`

**Dependencies:** `fs/promises`, `path`, `zod/v4`, `../../services/mcp/envExpansion`, `../../types/plugin`, `../debug`, `../errors`, `../log`, `../slowOperations`, `./pluginDirectories`

**Main flow:** Entry: `loadPluginLspServers()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/lspRecommendation.ts` (374 lines)

**Exports:**
- `LspPluginRecommendation`
- `getMatchingLspPlugins()`
- `addToNeverSuggest()`
- `incrementIgnoredCount()`
- `isLspRecommendationsDisabled()`
- `resetIgnoredCount()`

**Dependencies:** `path`, `../binaryCheck`, `../config`, `../debug`, `./installedPluginsManager`

**Main flow:** Entry: `getMatchingLspPlugins()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/managedPlugins.ts` (27 lines)

**Exports:**
- `getManagedPluginNames()`

**Dependencies:** `../settings/settings`

**Main flow:** Entry: `getManagedPluginNames()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/marketplaceHelpers.ts` (592 lines)

**Exports:**
- `formatFailureDetails()`
- `getMarketplaceSourceDisplay()`
- `createPluginId()`
- `loadMarketplacesWithGracefulDegradation()`
- `formatMarketplaceLoadingErrors()`
- `getStrictKnownMarketplaces()`
- `getBlockedMarketplaces()`
- `getPluginTrustMessage()`
- `extractHostFromSource()`
- `getHostPatternsFromAllowlist()`
- `isSourceInBlocklist()`
- `isSourceAllowedByPolicy()`
- `formatSourceForDisplay()`
- `EmptyMarketplaceReason`
- `detectEmptyMarketplaceReason()`

**Dependencies:** `lodash-es/isEqual`, `../errors`, `../log`, `../settings/settings`, `../stringUtils`, `./gitAvailability`, `./marketplaceManager`, `./schemas`

**Main flow:** Entry: `formatFailureDetails()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/marketplaceManager.ts` (2643 lines)

**Exports:**
- `getMarketplacesCacheDir()`
- `clearMarketplacesCache()`
- `KnownMarketplacesConfig`
- `DeclaredMarketplace`
- `getDeclaredMarketplaces()`
- `getMarketplaceDeclaringSource()`
- `saveMarketplaceToSettings()`
- `loadKnownMarketplacesConfig()`
- `loadKnownMarketplacesConfigSafe()`
- `saveKnownMarketplacesConfig()`
- `registerSeedMarketplaces()`
- `gitPull()`
- `gitClone()`
- `MarketplaceProgressCallback`
- `reconcileSparseCheckout()`
- `addMarketplaceSource()`
- `removeMarketplaceSource()`
- `getMarketplaceCacheOnly()`
- `getMarketplace`
- `getPluginByIdCacheOnly()`
- `getPluginById()`
- `refreshAllMarketplaces()`
- `refreshMarketplace()`
- `setMarketplaceAutoUpdate()`
- `_test`

**Dependencies:** `axios`, `fs/promises`, `lodash-es/isEqual`, `lodash-es/memoize`, `path`, `../../services/analytics/growthbook`, `../debug`, `../envUtils`, `../execFileNoThrow`, `../fsOperations`

**Main flow:** Entry: `getMarketplacesCacheDir()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/mcpPluginIntegration.ts` (634 lines)

**Exports:**
- `loadPluginMcpServers()`
- `UnconfiguredChannel`
- `getUnconfiguredChannels()`
- `addPluginScopeToServers()`
- `extractMcpServersFromPlugins()`
- `resolvePluginMcpEnvironment()`
- `getPluginMcpServers()`

**Dependencies:** `path`, `../../services/mcp/envExpansion`, `../../types/plugin`, `../debug`, `../errors`, `../fsOperations`, `../slowOperations`, `./pluginDirectories`

**Main flow:** Entry: `loadPluginMcpServers()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/mcpbHandler.ts` (968 lines)

**Exports:**
- `UserConfigValues`
- `UserConfigSchema`
- `McpbLoadResult`
- `McpbNeedsConfigResult`
- `McpbCacheMetadata`
- `ProgressCallback`
- `isMcpbSource()`
- `loadMcpServerUserConfig()`
- `saveMcpServerUserConfig()`
- `validateUserConfig()`
- `checkMcpbChanged()`
- `loadMcpbFile()`

**Dependencies:** `axios`, `crypto`, `fs/promises`, `path`, `../../services/mcp/types`, `../debug`, `../dxt/helpers`, `../dxt/zip`, `../errors`, `../fsOperations`

**Main flow:** Entry: `isMcpbSource()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/officialMarketplace.ts` (25 lines)

**Exports:**
- `OFFICIAL_MARKETPLACE_SOURCE`
- `OFFICIAL_MARKETPLACE_NAME`

**Dependencies:** `./schemas`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/officialMarketplaceGcs.ts` (216 lines)

**Exports:**
- `fetchOfficialMarketplaceFromGcs()`
- `classifyGcsError()`

**Dependencies:** `axios`, `fs/promises`, `path`, `../../bootstrap/state`, `../../services/analytics/index`, `../debug`, `../dxt/zip`, `../errors`

**Main flow:** Entry: `fetchOfficialMarketplaceFromGcs()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/officialMarketplaceStartupCheck.ts` (439 lines)

**Exports:**
- `OfficialMarketplaceSkipReason`
- `isOfficialMarketplaceAutoInstallDisabled()`
- `RETRY_CONFIG`
- `OfficialMarketplaceCheckResult`
- `checkAndInstallOfficialMarketplace()`

**Dependencies:** `path`, `../../services/analytics/growthbook`, `../../services/analytics/index`, `../config`, `../debug`, `../envUtils`, `../errors`, `../log`, `./gitAvailability`, `./marketplaceHelpers`

**Main flow:** Entry: `isOfficialMarketplaceAutoInstallDisabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/orphanedPluginFilter.ts` (114 lines)

**Exports:**
- `getGlobExclusionsForPluginCache()`
- `clearPluginCacheExclusions()`

**Dependencies:** `path`, `../ripgrep`, `./pluginDirectories`

**Main flow:** Entry: `getGlobExclusionsForPluginCache()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/parseMarketplaceInput.ts` (162 lines)

**Exports:**
- `parseMarketplaceInput()`

**Dependencies:** `os`, `path`, `../errors`, `../fsOperations`, `./schemas`

**Main flow:** Entry: `parseMarketplaceInput()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/performStartupChecks.tsx` (70 lines)

**Exports:**
- `performStartupChecks()`

**Dependencies:** `../../services/plugins/PluginInstallationManager`, `../../state/AppState`, `../config`, `../debug`, `./marketplaceManager`, `./pluginLoader`

**Main flow:** Entry: `performStartupChecks()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/pluginAutoupdate.ts` (284 lines)

**Exports:**
- `PluginAutoUpdateCallback`
- `onPluginsAutoUpdated()`
- `getAutoUpdatedPluginNames()`
- `updatePluginsForMarketplaces()`
- `autoUpdateMarketplacesAndPluginsInBackground()`

**Dependencies:** `../../services/plugins/pluginOperations`, `../config`, `../debug`, `../errors`, `../log`, `./pluginIdentifier`, `./schemas`

**Main flow:** Entry: `onPluginsAutoUpdated()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/pluginBlocklist.ts` (127 lines)

**Exports:**
- `detectDelistedPlugins()`
- `detectAndUninstallDelistedPlugins()`

**Dependencies:** `../../services/plugins/pluginOperations`, `../debug`, `../errors`, `./installedPluginsManager`, `./schemas`

**Main flow:** Entry: `detectDelistedPlugins()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/pluginDirectories.ts` (178 lines)

**Exports:**
- `getPluginsDirectory()`
- `getPluginSeedDirs()`
- `pluginDataDirPath()`
- `getPluginDataDir()`
- `getPluginDataDirSize()`
- `deletePluginDataDir()`

**Dependencies:** `fs`, `fs/promises`, `path`, `../../bootstrap/state`, `../debug`, `../envUtils`, `../errors`, `../format`, `../permissions/pathValidation`

**Main flow:** Entry: `getPluginsDirectory()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/pluginFlagging.ts` (208 lines)

**Exports:**
- `FlaggedPlugin`
- `loadFlaggedPlugins()`
- `getFlaggedPlugins()`
- `addFlaggedPlugin()`
- `markFlaggedPluginsSeen()`
- `removeFlaggedPlugin()`

**Dependencies:** `crypto`, `fs/promises`, `path`, `../debug`, `../fsOperations`, `../log`, `../slowOperations`, `./pluginDirectories`

**Main flow:** Entry: `loadFlaggedPlugins()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/pluginIdentifier.ts` (123 lines)

**Exports:**
- `ExtendedPluginScope`
- `PersistablePluginScope`
- `SETTING_SOURCE_TO_SCOPE`
- `ParsedPluginIdentifier`
- `parsePluginIdentifier()`
- `buildPluginId()`
- `isOfficialMarketplaceName()`
- `scopeToSettingSource()`
- `settingSourceToScope()`

**Dependencies:** local only

**Main flow:** Entry: `parsePluginIdentifier()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/pluginInstallationHelpers.ts` (595 lines)

**Exports:**
- `PluginInstallationInfo`
- `getCurrentTimestamp()`
- `validatePathWithinBase()`
- `cacheAndRegisterPlugin()`
- `registerPluginInstallation()`
- `parsePluginId()`
- `InstallCoreResult`
- `formatResolutionError()`
- `installResolvedPlugin()`
- `InstallPluginResult`
- `InstallPluginParams`
- `installPluginFromMarketplace()`

**Dependencies:** `crypto`, `fs/promises`, `path`, `../cwd`, `../errors`, `../fsOperations`, `../log`, `../telemetry/pluginTelemetry`, `./cacheUtils`, `./managedPlugins`

**Main flow:** Entry: `getCurrentTimestamp()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/pluginLoader.ts` (3302 lines)

**Exports:**
- `getPluginCachePath()`
- `getVersionedCachePathIn()`
- `getVersionedCachePath()`
- `getVersionedZipCachePath()`
- `probeSeedCacheAnyVersion()`
- `getLegacyCachePath()`
- `resolvePluginPath()`
- `copyDir()`
- `copyPluginToVersionedCache()`
- `installFromNpm()`
- `gitClone()`
- `installFromGitSubdir()`
- `generateTemporaryCacheNameForPlugin()`
- `cachePlugin()`
- `loadPluginManifest()`
- `createPluginFromPath()`
- `mergePluginSources()`
- `loadAllPlugins`
- `loadAllPluginsCacheOnly`
- `clearPluginCache()`
- `cachePluginSettings()`

**Dependencies:** `lodash-es/memoize`, `path`, `../../bootstrap/state`

**Main flow:** Entry: `getPluginCachePath()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/pluginOptionsStorage.ts` (400 lines)

**Exports:**
- `PluginOptionValues`
- `PluginOptionSchema`
- `getPluginStorageId()`
- `loadPluginOptions`
- `clearPluginOptionsCache()`
- `savePluginOptions()`
- `deletePluginOptions()`
- `getUnconfiguredOptions()`
- `substitutePluginVariables()`
- `substituteUserConfigVariables()`
- `substituteUserConfigInContent()`

**Dependencies:** `lodash-es/memoize`, `../../types/plugin`, `../debug`, `../log`, `../secureStorage/index`, `./pluginDirectories`

**Main flow:** Entry: `getPluginStorageId()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/pluginPolicy.ts` (20 lines)

**Exports:**
- `isPluginBlockedByPolicy()`

**Dependencies:** `../settings/settings`

**Main flow:** Entry: `isPluginBlockedByPolicy()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/pluginStartupCheck.ts` (341 lines)

**Exports:**
- `checkEnabledPlugins()`
- `getPluginEditableScopes()`
- `isPersistableScope()`
- `settingSourceToScope()`
- `getInstalledPlugins()`
- `findMissingPlugins()`
- `PluginInstallResult`
- `installSelectedPlugins()`

**Dependencies:** `path`, `../cwd`, `../debug`, `../log`, `../settings/constants`, `./addDirPluginSettings`, `./marketplaceManager`, `./schemas`

**Main flow:** Entry: `checkEnabledPlugins()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/pluginVersioning.ts` (157 lines)

**Exports:**
- `calculatePluginVersion()`
- `getGitCommitSha()`
- `getVersionFromPath()`
- `isVersionedPath()`

**Dependencies:** `crypto`, `../debug`, `../git/gitFilesystem`, `./schemas`

**Main flow:** Entry: `calculatePluginVersion()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/reconciler.ts` (265 lines)

**Exports:**
- `MarketplaceDiff`
- `diffMarketplaces()`
- `ReconcileOptions`
- `ReconcileProgressEvent`
- `ReconcileResult`
- `reconcileMarketplaces()`

**Dependencies:** `lodash-es/isEqual`, `path`, `../../bootstrap/state`, `../debug`, `../errors`, `../file`, `../git`, `../log`

**Main flow:** Entry: `diffMarketplaces()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/refresh.ts` (215 lines)

**Exports:**
- `RefreshActivePluginsResult`
- `refreshActivePlugins()`

**Dependencies:** `../../bootstrap/state`, `../../commands`, `../../services/lsp/manager`, `../../state/AppState`, `../../tools/AgentTool/loadAgentsDir`, `../../types/plugin`, `../debug`, `../errors`, `../log`

**Main flow:** Entry: `refreshActivePlugins()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/schemas.ts` (1681 lines)

**Exports:**
- `ALLOWED_OFFICIAL_MARKETPLACE_NAMES`
- `isMarketplaceAutoUpdate()`
- `BLOCKED_OFFICIAL_NAME_PATTERN`
- `isBlockedOfficialName()`
- `OFFICIAL_GITHUB_ORG`
- `validateOfficialNameSource()`
- `PluginAuthorSchema`
- `PluginHooksSchema`
- `CommandMetadataSchema`
- `LspServerConfigSchema`
- `PluginManifestSchema`
- `MarketplaceSourceSchema`
- `gitSha`
- `PluginSourceSchema`
- `isLocalPluginSource()`
- `isLocalMarketplaceSource()`
- `PluginMarketplaceEntrySchema`
- `PluginMarketplaceSchema`
- `PluginIdSchema`
- `DependencyRefSchema`
- `SettingsPluginEntrySchema`
- `InstalledPluginSchema`
- `InstalledPluginsFileSchemaV1`
- `PluginScopeSchema`
- `PluginInstallationEntrySchema`
- ... +20 more

**Dependencies:** `zod/v4`, `../../schemas/hooks`, `../../services/mcp/types`, `../lazySchema`

**Main flow:** Entry: `isMarketplaceAutoUpdate()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/validatePlugin.ts` (903 lines)

**Exports:**
- `ValidationResult`
- `ValidationError`
- `ValidationWarning`
- `validatePluginManifest()`
- `validateMarketplaceManifest()`
- `validatePluginContents()`
- `validateManifest()`

**Dependencies:** `fs`, `fs/promises`, `path`, `zod/v4`, `../errors`, `../frontmatterParser`, `../slowOperations`, `../yaml`

**Main flow:** Entry: `validatePluginManifest()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/walkPluginMarkdown.ts` (69 lines)

**Exports:**
- `walkPluginMarkdown()`

**Dependencies:** `path`, `../debug`, `../fsOperations`

**Main flow:** Entry: `walkPluginMarkdown()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/zipCache.ts` (406 lines)

**Exports:**
- `isPluginZipCacheEnabled()`
- `getPluginZipCachePath()`
- `getZipCacheKnownMarketplacesPath()`
- `getZipCacheInstalledPluginsPath()`
- `getZipCacheMarketplacesDir()`
- `getZipCachePluginsDir()`
- `getSessionPluginCachePath()`
- `cleanupSessionPluginCache()`
- `resetSessionPluginCache()`
- `atomicWriteToZipCache()`
- `createZipFromDirectory()`
- `extractZipToDirectory()`
- `convertDirectoryToZipInPlace()`
- `getMarketplaceJsonRelativePath()`
- `isMarketplaceSourceSupportedByZipCache()`

**Dependencies:** `crypto`, `os`, `path`, `../debug`, `../dxt/zip`, `../envUtils`, `../fsOperations`, `../permissions/pathValidation`, `./schemas`

**Main flow:** Entry: `isPluginZipCacheEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/plugins/zipCacheAdapters.ts` (164 lines)

**Exports:**
- `readZipCacheKnownMarketplaces()`
- `writeZipCacheKnownMarketplaces()`
- `readMarketplaceJson()`
- `saveMarketplaceJsonToZipCache()`
- `syncMarketplacesToZipCache()`

**Dependencies:** `fs/promises`, `path`, `../debug`, `../slowOperations`, `./marketplaceManager`

**Main flow:** Entry: `readZipCacheKnownMarketplaces()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/powershell/dangerousCmdlets.ts` (185 lines)

**Exports:**
- `FILEPATH_EXECUTION_CMDLETS`
- `DANGEROUS_SCRIPT_BLOCK_CMDLETS`
- `MODULE_LOADING_CMDLETS`
- `NETWORK_CMDLETS`
- `ALIAS_HIJACK_CMDLETS`
- `WMI_CIM_CMDLETS`
- `ARG_GATED_CMDLETS`
- `NEVER_SUGGEST`

**Dependencies:** `../permissions/dangerousPatterns`, `./parser`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/powershell/parser.ts` (1804 lines)

**Exports:**
- `CommandElementChild`
- `ParsedCommandElement`
- `ParsedPowerShellCommand`
- `RawCommandElement`
- `RawRedirection`
- `RawPipelineElement`
- `RawStatement`
- `PARSE_SCRIPT_BODY`
- `WINDOWS_MAX_COMMAND_LENGTH`
- `MAX_COMMAND_LENGTH`
- `mapStatementType()`
- `mapElementType()`
- `classifyCommandName()`
- `stripModulePrefix()`
- `transformCommandAst()`
- `transformExpressionElement()`
- `transformRedirection()`
- `transformStatement()`
- `COMMON_ALIASES`
- `getAllCommandNames()`
- `getAllCommands()`
- `getAllRedirections()`
- `getVariablesByScope()`
- `hasCommandNamed()`
- `hasDirectoryChange()`
- ... +9 more

**Dependencies:** `execa`, `../debug`, `../memoize`, `../shell/powershellDetection`, `../slowOperations`

**Main flow:** Entry: `mapStatementType()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/powershell/staticPrefix.ts` (316 lines)

**Exports:**
- `getCommandPrefixStatic()`
- `getCompoundCommandPrefixesStatic()`

**Dependencies:** `../bash/registry`, `../shell/specPrefix`, `../stringUtils`, `./dangerousCmdlets`

**Main flow:** Entry: `getCommandPrefixStatic()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/preflightChecks.tsx` (151 lines)

**Exports:**
- `PreflightCheckResult`
- `PreflightStep()`

**Dependencies:** `react/compiler-runtime`, `axios`, `react`, `src/services/analytics/index`, `../components/Spinner`, `../constants/oauth`, `../hooks/useTimeout`, `../ink`, `../services/api/errorUtils`, `./http`

**Main flow:** Entry: `PreflightStep()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/processUserInput/processBashCommand.tsx` (140 lines)

**Exports:**
- `processBashCommand()`

**Dependencies:** `@anthropic-ai/sdk/resources`, `crypto`, `react`, `src/components/BashModeProgress`, `src/Tool`, `src/tools/BashTool/BashTool`, `src/types/message`, `src/types/tools`, `../../services/analytics/index`, `../errors`

**Main flow:** Entry: `processBashCommand()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/processUserInput/processSlashCommand.tsx` (922 lines)

**Exports:**
- `looksLikeCommand()`
- `processSlashCommand()`
- `formatSkillLoadingMetadata()`
- `processPromptSlashCommand()`

**Dependencies:** `bun:bundle`, `@anthropic-ai/sdk/resources`, `crypto`, `src/bootstrap/state`, `src/commands`, `src/constants/messages`, `src/Tool`, `src/types/message`, `../../bootstrap/state`, `../../constants/xml`

**Feature gates:** `COORDINATOR_MODE`, `KAIROS`

**Main flow:** Entry: `looksLikeCommand()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/processUserInput/processTextPrompt.ts` (100 lines)

**Exports:**
- `processTextPrompt()`

**Dependencies:** `@anthropic-ai/sdk/resources`, `crypto`, `src/bootstrap/state`, `../../services/analytics/index`, `../../types/permissions`, `../messages`, `../telemetry/events`, `../telemetry/sessionTracing`

**Main flow:** Entry: `processTextPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/processUserInput/processUserInput.ts` (605 lines)

**Exports:**
- `ProcessUserInputContext`
- `ProcessUserInputBaseResult`
- `processUserInput()`

**Dependencies:** `bun:bundle`, `crypto`, `src/constants/querySource`, `src/services/analytics/index`, `src/utils/messages`, `../../hooks/useCanUseTool`, `../../hooks/useIdeSelection`, `../../Tool`, `../../types/permissions`, `../config`

**Feature gates:** `ULTRAPLAN`

**Main flow:** Entry: `processUserInput()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/sandbox/sandbox-adapter.ts` (985 lines)

**Exports:**
- `resolvePathPatternForSandbox()`
- `resolveSandboxFilesystemPath()`
- `shouldAllowManagedSandboxDomainsOnly()`
- `convertToSandboxRuntimeConfig()`
- `addToExcludedCommands()`
- `ISandboxManager`
- `SandboxManager`

**Dependencies:** `fs`, `fs/promises`, `lodash-es`, `path`, `../debug`, `../path`, `../platform`, `../settings/changeDetector`, `../settings/constants`, `../settings/managedPath`

**Main flow:** Entry: `resolvePathPatternForSandbox()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/sandbox/sandbox-ui-utils.ts` (12 lines)

**Exports:**
- `removeSandboxViolationTags()`

**Dependencies:** local only

**Main flow:** Entry: `removeSandboxViolationTags()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/secureStorage/fallbackStorage.ts` (70 lines)

**Exports:**
- `createFallbackStorage()`

**Dependencies:** `./types`

**Main flow:** Entry: `createFallbackStorage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/secureStorage/index.ts` (17 lines)

**Exports:**
- `getSecureStorage()`

**Dependencies:** `./fallbackStorage`, `./macOsKeychainStorage`, `./plainTextStorage`, `./types`

**Main flow:** Entry: `getSecureStorage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/secureStorage/keychainPrefetch.ts` (116 lines)

**Exports:**
- `startKeychainPrefetch()`
- `ensureKeychainPrefetchCompleted()`
- `getLegacyApiKeyPrefetchResult()`
- `clearLegacyApiKeyPrefetch()`

**Dependencies:** `child_process`, `../envUtils`

**Main flow:** Entry: `startKeychainPrefetch()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/secureStorage/macOsKeychainHelpers.ts` (111 lines)

**Exports:**
- `CREDENTIALS_SERVICE_SUFFIX`
- `getMacOsKeychainStorageServiceName()`
- `getUsername()`
- `KEYCHAIN_CACHE_TTL_MS`
- `keychainCacheState`
- `clearKeychainCache()`
- `primeKeychainCacheFromPrefetch()`

**Dependencies:** `crypto`, `os`, `src/constants/oauth`, `../envUtils`, `./types`

**Main flow:** Entry: `getMacOsKeychainStorageServiceName()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/secureStorage/macOsKeychainStorage.ts` (231 lines)

**Exports:**
- `macOsKeychainStorage`
- `isMacOsKeychainLocked()`

**Dependencies:** `execa`, `../debug`, `../execFileNoThrow`, `../execFileNoThrowPortable`, `../slowOperations`, `./types`

**Main flow:** Entry: `isMacOsKeychainLocked()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/secureStorage/plainTextStorage.ts` (84 lines)

**Exports:**
- `plainTextStorage`

**Dependencies:** `fs`, `path`, `../envUtils`, `../errors`, `../fsOperations`, `./types`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/allErrors.ts` (32 lines)

**Exports:**
- `getSettingsWithAllErrors()`

**Dependencies:** `../../services/mcp/config`, `./settings`, `./validation`

**Main flow:** Entry: `getSettingsWithAllErrors()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/applySettingsChange.ts` (92 lines)

**Exports:**
- `applySettingsChange()`

**Dependencies:** `../../state/AppState`, `../debug`, `../hooks/hooksConfigSnapshot`, `../permissions/permissions`, `../permissions/permissionsLoader`, `./constants`, `./settings`

**Main flow:** Entry: `applySettingsChange()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/changeDetector.ts` (488 lines)

**Exports:**
- `initialize()`
- `dispose()`
- `subscribe`
- `notifyChange()`
- `resetForTesting()`
- `settingsChangeDetector`

**Dependencies:** `chokidar`, `fs/promises`, `path`, `../../bootstrap/state`, `../cleanupRegistry`, `../debug`, `../errors`, `../signal`, `../slowOperations`, `./constants`

**Main flow:** Entry: `initialize()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/constants.ts` (202 lines)

**Exports:**
- `SETTING_SOURCES`
- `SettingSource`
- `getSettingSourceName()`
- `getSourceDisplayName()`
- `getSettingSourceDisplayNameLowercase()`
- `getSettingSourceDisplayNameCapitalized()`
- `parseSettingSourcesFlag()`
- `getEnabledSettingSources()`
- `isSettingSourceEnabled()`
- `EditableSettingSource`
- `SOURCES`
- `CLAUDE_CODE_SETTINGS_SCHEMA_URL`

**Dependencies:** `../../bootstrap/state`

**Main flow:** Entry: `getSettingSourceName()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/internalWrites.ts` (37 lines)

**Exports:**
- `markInternalWrite()`
- `consumeInternalWrite()`
- `clearInternalWrites()`

**Dependencies:** local only

**Main flow:** Entry: `markInternalWrite()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/managedPath.ts` (34 lines)

**Exports:**
- `getManagedFilePath`
- `getManagedSettingsDropInDir`

**Dependencies:** `lodash-es/memoize`, `path`, `../platform`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/mdm/constants.ts` (81 lines)

**Exports:**
- `MACOS_PREFERENCE_DOMAIN`
- `WINDOWS_REGISTRY_KEY_PATH_HKLM`
- `WINDOWS_REGISTRY_KEY_PATH_HKCU`
- `WINDOWS_REGISTRY_VALUE_NAME`
- `PLUTIL_PATH`
- `PLUTIL_ARGS_PREFIX`
- `MDM_SUBPROCESS_TIMEOUT_MS`
- `getMacOSPlistPaths()`

**Dependencies:** `os`, `path`

**Main flow:** Entry: `getMacOSPlistPaths()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/mdm/rawRead.ts` (130 lines)

**Exports:**
- `RawReadResult`
- `fireRawRead()`
- `startMdmRawRead()`
- `getMdmRawReadPromise()`

**Dependencies:** `child_process`, `fs`

**Main flow:** Entry: `fireRawRead()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/mdm/settings.ts` (316 lines)

**Exports:**
- `startMdmSettingsLoad()`
- `ensureMdmSettingsLoaded()`
- `getMdmSettings()`
- `getHkcuSettings()`
- `clearMdmSettingsCache()`
- `setMdmSettingsCache()`
- `refreshMdmSettings()`
- `parseCommandOutputAsSettings()`
- `parseRegQueryStdout()`

**Dependencies:** `path`, `../../debug`, `../../diagLogs`, `../../fileRead`, `../../fsOperations`, `../../json`, `../../startupProfiler`, `../types`

**Main flow:** Entry: `startMdmSettingsLoad()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/permissionValidation.ts` (262 lines)

**Exports:**
- `validatePermissionRule()`
- `PermissionRuleSchema`

**Dependencies:** `zod/v4`, `../../services/mcp/mcpStringUtils`, `../lazySchema`, `../permissions/permissionRuleParser`, `../stringUtils`

**Main flow:** Entry: `validatePermissionRule()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/pluginOnlyPolicy.ts` (60 lines)

**Exports:**
- `CustomizationSurface`
- `isRestrictedToPluginOnly()`
- `isSourceAdminTrusted()`

**Dependencies:** `./settings`, `./types`

**Main flow:** Entry: `isRestrictedToPluginOnly()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/schemaOutput.ts` (8 lines)

**Exports:**
- `generateSettingsJSONSchema()`

**Dependencies:** `zod/v4`, `../slowOperations`, `./types`

**Main flow:** Entry: `generateSettingsJSONSchema()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/settings.ts` (1015 lines)

**Exports:**
- `loadManagedFileSettings()`
- `getManagedFileSettingsPresence()`
- `parseSettingsFile()`
- `getSettingsRootPathForSource()`
- `getSettingsFilePathForSource()`
- `getRelativeSettingsFilePathForSource()`
- `getSettingsForSource()`
- `getPolicySettingsOrigin()`
- `updateSettingsForSource()`
- `settingsMergeCustomizer()`
- `getManagedSettingsKeysForLogging()`
- `getInitialSettings()`
- `getSettings_DEPRECATED`
- `SettingsWithSources`
- `getSettingsWithSources()`
- `getSettingsWithErrors()`
- `hasSkipDangerousModePermissionPrompt()`
- `hasAutoModeOptIn()`
- `getUseAutoModeDuringPlan()`
- `getAutoModeConfig()`
- `rawSettingsContainsKey()`

**Dependencies:** `bun:bundle`, `lodash-es/mergeWith`, `path`, `zod/v4`, `../../services/remoteManagedSettings/syncCacheState`, `../array`, `../debug`, `../diagLogs`, `../envUtils`, `../errors`

**Feature gates:** `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `loadManagedFileSettings()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/settingsCache.ts` (80 lines)

**Exports:**
- `getSessionSettingsCache()`
- `setSessionSettingsCache()`
- `getCachedSettingsForSource()`
- `setCachedSettingsForSource()`
- `getCachedParsedFile()`
- `setCachedParsedFile()`
- `resetSettingsCache()`
- `getPluginSettingsBase()`
- `setPluginSettingsBase()`
- `clearPluginSettingsBase()`

**Dependencies:** `./constants`, `./types`, `./validation`

**Main flow:** Entry: `getSessionSettingsCache()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/toolValidationConfig.ts` (103 lines)

**Exports:**
- `ToolValidationConfig`
- `TOOL_VALIDATION_CONFIG`
- `isFilePatternTool()`
- `isBashPrefixTool()`
- `getCustomValidation()`

**Dependencies:** local only

**Main flow:** Entry: `isFilePatternTool()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/types.ts` (1148 lines)

**Exports:**
- `EnvironmentVariablesSchema`
- `PermissionsSchema`
- `ExtraKnownMarketplaceSchema`
- `AllowedMcpServerEntrySchema`
- `DeniedMcpServerEntrySchema`
- `CUSTOMIZATION_SURFACES`
- `SettingsSchema`
- `PluginHookMatcher`
- `SkillHookMatcher`
- `AllowedMcpServerEntry`
- `DeniedMcpServerEntry`
- `SettingsJson`
- `isMcpServerNameEntry()`
- `isMcpServerCommandEntry()`
- `isMcpServerUrlEntry()`
- `UserConfigValues`
- `PluginConfig`

**Dependencies:** `bun:bundle`, `zod/v4`, `../../entrypoints/sandboxTypes`, `../envUtils`, `../lazySchema`, `../plugins/schemas`, `./constants`, `./permissionValidation`, `../../schemas/hooks`, `../array`

**Feature gates:** `KAIROS`, `KAIROS_BRIEF`, `LODESTONE`, `PROACTIVE`, `TRANSCRIPT_CLASSIFIER`, `VOICE_MODE`

**Main flow:** Entry: `isMcpServerNameEntry()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/validateEditTool.ts` (45 lines)

**Exports:**
- `validateInputForSettingsFileEdit()`

**Dependencies:** `src/Tool`, `../permissions/filesystem`, `./validation`

**Main flow:** Entry: `validateInputForSettingsFileEdit()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/validation.ts` (265 lines)

**Exports:**
- `FieldPath`
- `ValidationError`
- `SettingsWithErrors`
- `formatZodError()`
- `validateSettingsFileContent()`
- `filterInvalidPermissionRules()`

**Dependencies:** `src/services/mcp/types`, `zod/v4`, `../slowOperations`, `../stringUtils`, `./permissionValidation`, `./schemaOutput`, `./types`, `./validationTips`

**Main flow:** Entry: `formatZodError()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/settings/validationTips.ts` (164 lines)

**Exports:**
- `ValidationTip`
- `TipContext`
- `getValidationTip()`

**Dependencies:** `zod/v4`

**Main flow:** Entry: `getValidationTip()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/shell/bashProvider.ts` (255 lines)

**Exports:**
- `createBashShellProvider()`

**Dependencies:** `bun:bundle`, `fs/promises`, `os`, `path`, `path/posix`, `../bash/bashPipeCommand`, `../bash/ShellSnapshot`, `../bash/shellPrefix`, `../bash/shellQuote`, `../debug`

**Feature gates:** `COMMIT_ATTRIBUTION`

**Main flow:** Entry: `createBashShellProvider()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/shell/outputLimits.ts` (14 lines)

**Exports:**
- `BASH_MAX_OUTPUT_UPPER_LIMIT`
- `BASH_MAX_OUTPUT_DEFAULT`
- `getMaxOutputLength()`

**Dependencies:** `../envValidation`

**Main flow:** Entry: `getMaxOutputLength()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/shell/powershellDetection.ts` (107 lines)

**Exports:**
- `findPowerShell()`
- `getCachedPowerShellPath()`
- `PowerShellEdition`
- `getPowerShellEdition()`
- `resetPowerShellCache()`

**Dependencies:** `fs/promises`, `../platform`, `../which`

**Main flow:** Entry: `findPowerShell()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/shell/powershellProvider.ts` (123 lines)

**Exports:**
- `buildPowerShellArgs()`
- `createPowerShellProvider()`

**Dependencies:** `os`, `path`, `path/posix`, `../sessionEnvVars`, `./shellProvider`

**Main flow:** Entry: `buildPowerShellArgs()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/shell/prefix.ts` (367 lines)

**Exports:**
- `CommandPrefixResult`
- `CommandSubcommandPrefixResult`
- `PrefixExtractorConfig`
- `createCommandPrefixExtractor()`
- `createSubcommandPrefixExtractor()`

**Dependencies:** `chalk`, `../../constants/querySource`, `../../services/analytics/growthbook`, `../../services/api/claude`, `../../services/api/errors`, `../memoize`, `../slowOperations`, `../systemPromptType`

**Main flow:** Entry: `createCommandPrefixExtractor()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/shell/readOnlyCommandValidation.ts` (1893 lines)

**Exports:**
- `FlagArgType`
- `ExternalCommandConfig`
- `GIT_READ_ONLY_COMMANDS`
- `GH_READ_ONLY_COMMANDS`
- `DOCKER_READ_ONLY_COMMANDS`
- `RIPGREP_READ_ONLY_COMMANDS`
- `PYRIGHT_READ_ONLY_COMMANDS`
- `EXTERNAL_READONLY_COMMANDS`
- `containsVulnerableUncPath()`
- `FLAG_PATTERN`
- `validateFlagArgument()`
- `validateFlags()`

**Dependencies:** `../platform`

**Main flow:** Entry: `containsVulnerableUncPath()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/shell/resolveDefaultShell.ts` (14 lines)

**Exports:**
- `resolveDefaultShell()`

**Dependencies:** `../settings/settings`

**Main flow:** Entry: `resolveDefaultShell()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/shell/shellProvider.ts` (33 lines)

**Exports:**
- `SHELL_TYPES`
- `ShellType`
- `DEFAULT_HOOK_SHELL`
- `ShellProvider`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/shell/shellToolUtils.ts` (22 lines)

**Exports:**
- `SHELL_TOOL_NAMES`
- `isPowerShellToolEnabled()`

**Dependencies:** `../../tools/BashTool/toolName`, `../../tools/PowerShellTool/toolName`, `../envUtils`, `../platform`

**Main flow:** Entry: `isPowerShellToolEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/shell/specPrefix.ts` (241 lines)

**Exports:**
- `DEPTH_RULES`
- `buildPrefix()`

**Dependencies:** `../bash/registry`

**Main flow:** Entry: `buildPrefix()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/skills/skillChangeDetector.ts` (311 lines)

**Exports:**
- `initialize()`
- `dispose()`
- `subscribe`
- `resetForTesting()`
- `skillChangeDetector`

**Dependencies:** `chokidar`, `path`, `../../bootstrap/state`, `../attachments`, `../cleanupRegistry`, `../debug`, `../fsOperations`, `../hooks`, `../signal`

**Main flow:** Entry: `initialize()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/staticRender.tsx` (116 lines)

**Exports:**
- `renderToAnsiString()`
- `renderToString()`

**Dependencies:** `react/compiler-runtime`, `react`, `stream`, `strip-ansi`, `../ink`

**Main flow:** Entry: `renderToAnsiString()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/status.tsx` (362 lines)

**Exports:**
- `Property`
- `Diagnostic`
- `buildSandboxProperties()`
- `buildIDEProperties()`
- `buildMcpProperties()`
- `buildMemoryDiagnostics()`
- `buildSettingSourcesProperties()`
- `buildInstallationDiagnostics()`
- `buildInstallationHealthDiagnostics()`
- `buildAccountProperties()`
- `buildAPIProviderProperties()`
- `getModelDisplayLabel()`

**Dependencies:** `chalk`, `figures`, `react`, `../ink`, `../services/mcp/types`, `./auth`, `./claudemd`, `./doctorDiagnostic`, `./envUtils`, `./file`

**Main flow:** Entry: `buildSandboxProperties()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/statusNoticeDefinitions.tsx` (198 lines)

**Exports:**
- `StatusNoticeType`
- `StatusNoticeContext`
- `StatusNoticeDefinition`
- `statusNoticeDefinitions`
- `getActiveNotices()`

**Dependencies:** `../ink`, `react`, `./claudemd`, `figures`, `./cwd`, `path`, `./format`, `./config`, `./auth`, `../tools/AgentTool/loadAgentsDir`

**Main flow:** Entry: `getActiveNotices()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/suggestions/commandSuggestions.ts` (567 lines)

**Exports:**
- `MidInputSlashCommand`
- `findMidInputSlashCommand()`
- `getBestCommandMatch()`
- `isCommandInput()`
- `hasCommandArgs()`
- `formatCommand()`
- `generateCommandSuggestions()`
- `applyCommandSuggestion()`
- `findSlashCommandPositions()`

**Dependencies:** `fuse`, `../../components/PromptInput/PromptInputFooterSuggestions`, `./skillUsageTracking`

**Main flow:** Entry: `findMidInputSlashCommand()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/suggestions/directoryCompletion.ts` (263 lines)

**Exports:**
- `DirectoryEntry`
- `PathEntry`
- `CompletionOptions`
- `PathCompletionOptions`
- `parsePartialPath()`
- `scanDirectory()`
- `getDirectoryCompletions()`
- `clearDirectoryCache()`
- `isPathLikeToken()`
- `scanDirectoryForPaths()`
- `getPathCompletions()`
- `clearPathCache()`

**Dependencies:** `lru-cache`, `path`, `src/components/PromptInput/PromptInputFooterSuggestions`, `src/utils/cwd`, `src/utils/fsOperations`, `src/utils/log`, `src/utils/path`

**Main flow:** Entry: `parsePartialPath()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/suggestions/shellHistoryCompletion.ts` (119 lines)

**Exports:**
- `ShellHistoryMatch`
- `clearShellHistoryCache()`
- `prependToShellHistoryCache()`
- `getShellHistoryCompletion()`

**Dependencies:** `../../history`, `../debug`

**Main flow:** Entry: `clearShellHistoryCache()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/suggestions/skillUsageTracking.ts` (55 lines)

**Exports:**
- `recordSkillUsage()`
- `getSkillUsageScore()`

**Dependencies:** `../config`

**Main flow:** Entry: `recordSkillUsage()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/suggestions/slackChannelSuggestions.ts` (209 lines)

**Exports:**
- `subscribeKnownChannels`
- `hasSlackMcpServer()`
- `getKnownChannelsVersion()`
- `findSlackChannelPositions()`
- `getSlackChannelSuggestions()`
- `clearSlackChannelCache()`

**Dependencies:** `zod`, `../../components/PromptInput/PromptInputFooterSuggestions`, `../../services/mcp/types`, `../debug`, `../lazySchema`, `../signal`, `../slowOperations`

**Main flow:** Entry: `hasSlackMcpServer()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/It2SetupPrompt.tsx` (380 lines)

**Exports:**
- `It2SetupPrompt()`

**Dependencies:** `react/compiler-runtime`, `react`, `../../components/CustomSelect/index`, `../../components/design-system/Pane`, `../../components/Spinner`, `../../hooks/useExitOnCtrlCDWithKeybindings`, `../../ink`, `../../keybindings/useKeybinding`, `./backends/it2Setup`

**Main flow:** Entry: `It2SetupPrompt()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/backends/ITermBackend.ts` (370 lines)

**Exports:**
- `ITermBackend`

**Dependencies:** `../../../tools/AgentTool/agentColorManager`, `../../../utils/debug`, `../../../utils/execFileNoThrow`, `./detection`, `./registry`, `./types`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/backends/InProcessBackend.ts` (339 lines)

**Exports:**
- `InProcessBackend`
- `createInProcessBackend()`

**Dependencies:** `../../../Tool`, `../../../utils/agentId`, `../../../utils/debug`, `../../../utils/slowOperations`, `../inProcessRunner`

**Main flow:** Entry: `createInProcessBackend()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/backends/PaneBackendExecutor.ts` (354 lines)

**Exports:**
- `PaneBackendExecutor`
- `createPaneBackendExecutor()`

**Dependencies:** `../../../bootstrap/state`, `../../../Tool`, `../../../utils/agentId`, `../../../utils/bash/shellQuote`, `../../../utils/cleanupRegistry`, `../../../utils/debug`, `../../../utils/slowOperations`, `../../../utils/teammateMailbox`, `../teammateLayoutManager`, `./detection`

**Main flow:** Entry: `createPaneBackendExecutor()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/backends/TmuxBackend.ts` (764 lines)

**Exports:**
- `TmuxBackend`

**Dependencies:** `../../../tools/AgentTool/agentColorManager`, `../../../utils/debug`, `../../../utils/execFileNoThrow`, `../../../utils/log`, `../../array`, `../../sleep`, `./registry`, `./types`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/backends/detection.ts` (128 lines)

**Exports:**
- `isInsideTmuxSync()`
- `isInsideTmux()`
- `getLeaderPaneId()`
- `isTmuxAvailable()`
- `isInITerm2()`
- `IT2_COMMAND`
- `isIt2CliAvailable()`
- `resetDetectionCache()`

**Dependencies:** `../../../utils/env`, `../../../utils/execFileNoThrow`, `../constants`

**Main flow:** Entry: `isInsideTmuxSync()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/backends/it2Setup.ts` (245 lines)

**Exports:**
- `PythonPackageManager`
- `It2InstallResult`
- `It2VerifyResult`
- `detectPythonPackageManager()`
- `isIt2CliAvailable()`
- `installIt2()`
- `verifyIt2Setup()`
- `getPythonApiInstructions()`
- `markIt2SetupComplete()`
- `setPreferTmuxOverIterm2()`
- `getPreferTmuxOverIterm2()`

**Dependencies:** `os`, `../../../utils/config`, `../../../utils/debug`, `../../../utils/log`

**Main flow:** Entry: `detectPythonPackageManager()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/backends/registry.ts` (464 lines)

**Exports:**
- `ensureBackendsRegistered()`
- `registerTmuxBackend()`
- `registerITermBackend()`
- `detectAndGetBackend()`
- `getBackendByType()`
- `getCachedBackend()`
- `getCachedDetectionResult()`
- `markInProcessFallback()`
- `isInProcessEnabled()`
- `getResolvedTeammateMode()`
- `getInProcessBackend()`
- `getTeammateExecutor()`
- `resetBackendDetection()`

**Dependencies:** `../../../bootstrap/state`, `../../../utils/debug`, `../../../utils/platform`, `./InProcessBackend`, `./it2Setup`, `./PaneBackendExecutor`, `./teammateModeSnapshot`

**Main flow:** Entry: `ensureBackendsRegistered()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/backends/teammateModeSnapshot.ts` (87 lines)

**Exports:**
- `TeammateMode`
- `setCliTeammateModeOverride()`
- `getCliTeammateModeOverride()`
- `clearCliTeammateModeOverride()`
- `captureTeammateModeSnapshot()`
- `getTeammateModeFromSnapshot()`

**Dependencies:** `../../../utils/config`, `../../../utils/debug`, `../../../utils/log`

**Main flow:** Entry: `setCliTeammateModeOverride()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/backends/types.ts` (311 lines)

**Exports:**
- `BackendType`
- `PaneBackendType`
- `PaneId`
- `CreatePaneResult`
- `PaneBackend`
- `BackendDetectionResult`
- `TeammateIdentity`
- `TeammateSpawnConfig`
- `TeammateSpawnResult`
- `TeammateMessage`
- `TeammateExecutor`
- `isPaneBackend()`

**Dependencies:** `../../../tools/AgentTool/agentColorManager`

**Main flow:** Entry: `isPaneBackend()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/constants.ts` (33 lines)

**Exports:**
- `TEAM_LEAD_NAME`
- `SWARM_SESSION_NAME`
- `SWARM_VIEW_WINDOW_NAME`
- `TMUX_COMMAND`
- `HIDDEN_SESSION_NAME`
- `getSwarmSocketName()`
- `TEAMMATE_COMMAND_ENV_VAR`
- `TEAMMATE_COLOR_ENV_VAR`
- `PLAN_MODE_REQUIRED_ENV_VAR`

**Dependencies:** local only

**Main flow:** Entry: `getSwarmSocketName()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/inProcessRunner.ts` (1552 lines)

**Exports:**
- `InProcessRunnerConfig`
- `InProcessRunnerResult`
- `runInProcessTeammate()`
- `startInProcessTeammate()`

**Dependencies:** `bun:bundle`, `@anthropic-ai/sdk/resources/messages.mjs`, `../../constants/prompts`, `../../constants/xml`, `../../hooks/useCanUseTool`, `../../services/compact/autoCompact`, `../../services/compact/microCompact`, `../../state/AppState`, `../../Tool`, `../../tasks/InProcessTeammateTask/InProcessTeammateTask`

**Feature gates:** `BASH_CLASSIFIER`

**Main flow:** Entry: `runInProcessTeammate()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/leaderPermissionBridge.ts` (54 lines)

**Exports:**
- `SetToolUseConfirmQueueFn`
- `SetToolPermissionContextFn`
- `registerLeaderToolUseConfirmQueue()`
- `getLeaderToolUseConfirmQueue()`
- `unregisterLeaderToolUseConfirmQueue()`
- `registerLeaderSetToolPermissionContext()`
- `getLeaderSetToolPermissionContext()`
- `unregisterLeaderSetToolPermissionContext()`

**Dependencies:** `../../components/permissions/PermissionRequest`, `../../Tool`

**Main flow:** Entry: `registerLeaderToolUseConfirmQueue()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/permissionSync.ts` (928 lines)

**Exports:**
- `SwarmPermissionRequestSchema`
- `SwarmPermissionRequest`
- `PermissionResolution`
- `getPermissionDir()`
- `generateRequestId()`
- `createPermissionRequest()`
- `writePermissionRequest()`
- `readPendingPermissions()`
- `readResolvedPermission()`
- `resolvePermission()`
- `cleanupOldResolutions()`
- `PermissionResponse`
- `pollForResponse()`
- `removeWorkerResponse()`
- `isTeamLeader()`
- `isSwarmWorker()`
- `deleteResolvedPermission()`
- `submitPermissionRequest`
- `getLeaderName()`
- `sendPermissionRequestViaMailbox()`
- `sendPermissionResponseViaMailbox()`
- `generateSandboxRequestId()`
- `sendSandboxPermissionRequestViaMailbox()`
- `sendSandboxPermissionResponseViaMailbox()`

**Dependencies:** `fs/promises`, `path`, `zod/v4`, `../debug`, `../errors`, `../lazySchema`, `../lockfile`, `../log`, `../permissions/PermissionUpdateSchema`, `../slowOperations`

**Main flow:** Entry: `getPermissionDir()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/reconnection.ts` (119 lines)

**Exports:**
- `computeInitialTeamContext()`
- `initializeTeammateContextFromSession()`

**Dependencies:** `../../state/AppState`, `../debug`, `../log`, `../teammate`, `./teamHelpers`

**Main flow:** Entry: `computeInitialTeamContext()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/spawnInProcess.ts` (328 lines)

**Exports:**
- `SpawnContext`
- `InProcessSpawnConfig`
- `InProcessSpawnOutput`
- `spawnInProcessTeammate()`
- `killInProcessTeammate()`

**Dependencies:** `lodash-es/sample`, `../../bootstrap/state`, `../../constants/spinnerVerbs`, `../../constants/turnCompletionVerbs`, `../../state/AppState`, `../../Task`, `../abortController`, `../agentId`, `../cleanupRegistry`, `../debug`

**Main flow:** Entry: `spawnInProcessTeammate()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/spawnUtils.ts` (146 lines)

**Exports:**
- `getTeammateCommand()`
- `buildInheritedCliFlags()`
- `buildInheritedEnvVars()`

**Dependencies:** `../bash/shellQuote`, `../bundledMode`, `../permissions/PermissionMode`, `./backends/teammateModeSnapshot`, `./constants`

**Main flow:** Entry: `getTeammateCommand()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/teamHelpers.ts` (683 lines)

**Exports:**
- `inputSchema`
- `SpawnTeamOutput`
- `CleanupOutput`
- `TeamAllowedPath`
- `TeamFile`
- `Input`
- `Output`
- `sanitizeName()`
- `sanitizeAgentName()`
- `getTeamDir()`
- `getTeamFilePath()`
- `readTeamFile()`
- `readTeamFileAsync()`
- `writeTeamFileAsync()`
- `removeTeammateFromTeamFile()`
- `addHiddenPaneId()`
- `removeHiddenPaneId()`
- `removeMemberFromTeam()`
- `removeMemberByAgentId()`
- `setMemberMode()`
- `syncTeammateMode()`
- `setMultipleMemberModes()`
- `setMemberActive()`
- `registerTeamForSessionCleanup()`
- `unregisterTeamForSessionCleanup()`
- ... +2 more

**Dependencies:** `fs`, `fs/promises`, `path`, `zod/v4`, `../../bootstrap/state`, `../debug`, `../envUtils`, `../errors`, `../execFileNoThrow`, `../git`

**Main flow:** Entry: `sanitizeName()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/teammateInit.ts` (129 lines)

**Exports:**
- `initializeTeammateHooks()`

**Dependencies:** `../../state/AppState`, `../debug`, `../hooks/sessionHooks`, `../permissions/PermissionUpdate`, `../slowOperations`, `../teammate`, `./teamHelpers`

**Main flow:** Entry: `initializeTeammateHooks()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/teammateLayoutManager.ts` (107 lines)

**Exports:**
- `assignTeammateColor()`
- `getTeammateColor()`
- `clearTeammateColors()`
- `isInsideTmux()`
- `createTeammatePaneInSwarmView()`
- `enablePaneBorderStatus()`
- `sendCommandToPane()`

**Dependencies:** `../../tools/AgentTool/agentColorManager`, `./backends/registry`, `./backends/types`

**Main flow:** Entry: `assignTeammateColor()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/teammateModel.ts` (10 lines)

**Exports:**
- `getHardcodedTeammateModelFallback()`

**Dependencies:** `../model/configs`, `../model/providers`

**Main flow:** Entry: `getHardcodedTeammateModelFallback()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/swarm/teammatePromptAddendum.ts` (18 lines)

**Exports:**
- `TEAMMATE_SYSTEM_PROMPT_ADDENDUM`

**Dependencies:** local only

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/task/TaskOutput.ts` (390 lines)

**Exports:**
- `TaskOutput`

**Dependencies:** `fs/promises`, `../CircularBuffer`, `../debug`, `../fsOperations`, `../shell/outputLimits`, `../stringUtils`, `./diskOutput`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/task/diskOutput.ts` (451 lines)

**Exports:**
- `MAX_TASK_OUTPUT_BYTES`
- `MAX_TASK_OUTPUT_BYTES_DISPLAY`
- `getTaskOutputDir()`
- `_resetTaskOutputDirForTest()`
- `getTaskOutputPath()`
- `DiskTaskOutput`
- `_clearOutputsForTest()`
- `appendTaskOutput()`
- `flushTaskOutput()`
- `evictTaskOutput()`
- `getTaskOutputDelta()`
- `getTaskOutput()`
- `getTaskOutputSize()`
- `cleanupTaskOutput()`
- `initTaskOutput()`
- `initTaskOutputAsSymlink()`

**Dependencies:** `fs`, `path`, `../../bootstrap/state`, `../errors`, `../fsOperations`, `../log`, `../permissions/filesystem`

**Main flow:** Entry: `getTaskOutputDir()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/task/framework.ts` (308 lines)

**Exports:**
- `POLL_INTERVAL_MS`
- `STOPPED_DISPLAY_MS`
- `PANEL_GRACE_MS`
- `TaskAttachment`
- `updateTaskState()`
- `registerTask()`
- `evictTerminalTask()`
- `getRunningTasks()`
- `generateTaskAttachments()`
- `applyTaskOffsetsAndEvictions()`
- `pollTasks()`

**Dependencies:** `../../state/AppState`, `../../tasks/types`, `../messageQueueManager`, `../sdkEventQueue`, `./diskOutput`

**Main flow:** Entry: `updateTaskState()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/task/outputFormatting.ts` (38 lines)

**Exports:**
- `TASK_MAX_OUTPUT_UPPER_LIMIT`
- `TASK_MAX_OUTPUT_DEFAULT`
- `getMaxTaskOutputLength()`
- `formatTaskOutput()`

**Dependencies:** `../envValidation`, `./diskOutput`

**Main flow:** Entry: `getMaxTaskOutputLength()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/task/sdkProgress.ts` (36 lines)

**Exports:**
- `emitTaskProgress()`

**Dependencies:** `../../types/tools`, `../sdkEventQueue`

**Main flow:** Entry: `emitTaskProgress()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/telemetry/betaSessionTracing.ts` (491 lines)

**Exports:**
- `clearBetaTracingState()`
- `isBetaTracingEnabled()`
- `truncateContent()`
- `LLMRequestNewContext`
- `addBetaInteractionAttributes()`
- `addBetaLLMRequestAttributes()`
- `addBetaLLMResponseAttributes()`
- `addBetaToolInputAttributes()`
- `addBetaToolResultAttributes()`

**Dependencies:** `@opentelemetry/api`, `crypto`, `../../bootstrap/state`, `../../services/analytics/growthbook`, `../../services/analytics/metadata`, `../../types/message`, `../envUtils`, `../slowOperations`, `./events`

**Main flow:** Entry: `clearBetaTracingState()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/telemetry/bigqueryExporter.ts` (252 lines)

**Exports:**
- `BigQueryMetricsExporter`

**Dependencies:** `@opentelemetry/api`, `@opentelemetry/core`, `axios`, `src/services/api/metricsOptOut`, `../../bootstrap/state`, `../auth`, `../config`, `../debug`, `../errors`, `../http`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/telemetry/events.ts` (75 lines)

**Exports:**
- `redactIfDisabled()`
- `logOTelEvent()`

**Dependencies:** `@opentelemetry/api`, `src/bootstrap/state`, `../debug`, `../envUtils`, `../telemetryAttributes`

**Main flow:** Entry: `redactIfDisabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/telemetry/instrumentation.ts` (825 lines)

**Exports:**
- `bootstrapTelemetry()`
- `parseExporterTypes()`
- `isTelemetryEnabled()`
- `initializeTelemetry()`
- `flushTelemetry()`

**Dependencies:** `@opentelemetry/api`, `@opentelemetry/api-logs`, `https-proxy-agent`, `src/utils/platform`, `../caCerts`

**Main flow:** Entry: `bootstrapTelemetry()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/telemetry/logger.ts` (26 lines)

**Exports:**
- `ClaudeCodeDiagLogger`

**Dependencies:** `@opentelemetry/api`, `../debug`, `../log`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/telemetry/perfettoTracing.ts` (1120 lines)

**Exports:**
- `TraceEventPhase`
- `TraceEvent`
- `initializePerfettoTracing()`
- `isPerfettoTracingEnabled()`
- `registerAgent()`
- `unregisterAgent()`
- `startLLMRequestPerfettoSpan()`
- `endLLMRequestPerfettoSpan()`
- `startToolPerfettoSpan()`
- `endToolPerfettoSpan()`
- `startUserInputPerfettoSpan()`
- `endUserInputPerfettoSpan()`
- `emitPerfettoInstant()`
- `emitPerfettoCounter()`
- `startInteractionPerfettoSpan()`
- `endInteractionPerfettoSpan()`
- `getPerfettoEvents()`
- `resetPerfettoTracer()`
- `triggerPeriodicWriteForTesting()`
- `evictStaleSpansForTesting()`
- `MAX_EVENTS_FOR_TESTING`
- `evictOldestEventsForTesting()`

**Dependencies:** `bun:bundle`, `fs`, `fs/promises`, `path`, `../../bootstrap/state`, `../cleanupRegistry`, `../debug`, `../errors`, `../hash`, `../slowOperations`

**Feature gates:** `PERFETTO_TRACING`

**Main flow:** Entry: `initializePerfettoTracing()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/telemetry/pluginTelemetry.ts` (289 lines)

**Exports:**
- `hashPluginId()`
- `TelemetryPluginScope`
- `getTelemetryPluginScope()`
- `EnabledVia`
- `InvocationTrigger`
- `SkillExecutionContext`
- `InstallSource`
- `getEnabledVia()`
- `buildPluginTelemetryFields()`
- `buildPluginCommandTelemetryFields()`
- `logPluginsEnabledForSession()`
- `PluginCommandErrorCategory`
- `classifyPluginCommandError()`
- `logPluginLoadErrors()`

**Dependencies:** `crypto`, `path`

**Main flow:** Entry: `hashPluginId()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/telemetry/sessionTracing.ts` (927 lines)

**Exports:**
- `isEnhancedTelemetryEnabled()`
- `startInteractionSpan()`
- `endInteractionSpan()`
- `startLLMRequestSpan()`
- `endLLMRequestSpan()`
- `startToolSpan()`
- `startToolBlockedOnUserSpan()`
- `endToolBlockedOnUserSpan()`
- `startToolExecutionSpan()`
- `endToolExecutionSpan()`
- `endToolSpan()`
- `addToolContentEvent()`
- `getCurrentSpan()`
- `executeInSpan()`
- `startHookSpan()`
- `endHookSpan()`

**Dependencies:** `bun:bundle`, `@opentelemetry/api`, `async_hooks`, `../../services/analytics/growthbook`, `../../types/message`, `../envUtils`, `../telemetryAttributes`

**Feature gates:** `ENHANCED_TELEMETRY_BETA`

**Main flow:** Entry: `isEnhancedTelemetryEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/telemetry/skillLoadedEvent.ts` (39 lines)

**Exports:**
- `logSkillsLoaded()`

**Dependencies:** `../../commands`, `../../tools/SkillTool/prompt`

**Main flow:** Entry: `logSkillsLoaded()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/teleport.tsx` (1226 lines)

**Exports:**
- `TeleportResult`
- `TeleportProgressStep`
- `TeleportProgressCallback`
- `validateGitState()`
- `processMessagesForTeleportResume()`
- `checkOutTeleportedSessionBranch()`
- `RepoValidationResult`
- `validateSessionRepository()`
- `teleportResumeCodeSession()`
- `teleportToRemoteWithErrorHandling()`
- `teleportFromSessionsAPI()`
- `PollRemoteSessionResponse`
- `pollRemoteSessionEvents()`
- `teleportToRemote()`
- `archiveRemoteSession()`

**Dependencies:** `axios`, `chalk`, `crypto`, `react`, `src/bootstrap/state`, `src/services/analytics/growthbook`, `src/services/analytics/index`, `src/services/policyLimits/index`, `zod/v4`, `../components/TeleportError`

**Main flow:** Entry: `validateGitState()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/teleport/api.ts` (466 lines)

**Exports:**
- `CCR_BYOC_BETA`
- `isTransientNetworkError()`
- `axiosGetWithRetry()`
- `SessionStatus`
- `GitSource`
- `KnowledgeBaseSource`
- `SessionContextSource`
- `OutcomeGitInfo`
- `GitRepositoryOutcome`
- `Outcome`
- `SessionContext`
- `SessionResource`
- `ListSessionsResponse`
- `CodeSessionSchema`
- `CodeSession`
- `prepareApiRequest()`
- `fetchCodeSessionsFromSessionsAPI()`
- `getOAuthHeaders()`
- `fetchSession()`
- `getBranchFromSession()`
- `RemoteMessageContent`
- `sendEventToRemoteSession()`
- `updateSessionTitle()`

**Dependencies:** `axios`, `crypto`, `src/constants/oauth`, `src/services/oauth/client`, `zod/v4`, `../auth`, `../debug`, `../detectRepository`, `../errors`, `../lazySchema`

**Main flow:** Entry: `isTransientNetworkError()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/teleport/environmentSelection.ts` (77 lines)

**Exports:**
- `EnvironmentSelectionInfo`
- `getEnvironmentSelectionInfo()`

**Dependencies:** `../settings/constants`, `./environments`

**Main flow:** Entry: `getEnvironmentSelectionInfo()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/teleport/environments.ts` (120 lines)

**Exports:**
- `EnvironmentKind`
- `EnvironmentState`
- `EnvironmentResource`
- `EnvironmentListResponse`
- `fetchEnvironments()`
- `createDefaultCloudEnvironment()`

**Dependencies:** `axios`, `src/constants/oauth`, `src/services/oauth/client`, `../auth`, `../errors`, `../log`, `./api`

**Main flow:** Entry: `fetchEnvironments()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/teleport/gitBundle.ts` (292 lines)

**Exports:**
- `BundleUploadResult`
- `createAndUploadGitBundle()`

**Dependencies:** `fs/promises`, `../../services/analytics/growthbook`, `../../services/api/filesApi`, `../cwd`, `../debug`, `../execFileNoThrow`, `../git`, `../tempfile`

**Main flow:** Entry: `createAndUploadGitBundle()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/todo/types.ts` (18 lines)

**Exports:**
- `TodoItemSchema`
- `TodoItem`
- `TodoListSchema`
- `TodoList`

**Dependencies:** `zod/v4`, `../lazySchema`

**Main flow:** Module-level utilities and side effects.

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/ultraplan/ccrSession.ts` (349 lines)

**Exports:**
- `PollFailReason`
- `UltraplanPollError`
- `ULTRAPLAN_TELEPORT_SENTINEL`
- `ScanResult`
- `UltraplanPhase`
- `ExitPlanModeScanner`
- `PollResult`
- `pollForApprovedExitPlanMode()`

**Dependencies:** `../../entrypoints/agentSdkTypes`, `../../tools/ExitPlanModeTool/constants`, `../debug`, `../sleep`, `../teleport/api`

**Main flow:** Entry: `pollForApprovedExitPlanMode()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `utils/ultraplan/keyword.ts` (127 lines)

**Exports:**
- `findUltraplanTriggerPositions()`
- `findUltrareviewTriggerPositions()`
- `hasUltraplanKeyword()`
- `hasUltrareviewKeyword()`
- `replaceUltraplanKeyword()`

**Dependencies:** local only

**Main flow:** Entry: `findUltraplanTriggerPositions()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `vim/motions.ts` (82 lines)

**Exports:**
- `resolveMotion()`
- `isInclusiveMotion()`
- `isLinewiseMotion()`

**Dependencies:** `../utils/Cursor`

**Main flow:** Entry: `resolveMotion()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `vim/operators.ts` (556 lines)

**Exports:**
- `OperatorContext`
- `executeOperatorMotion()`
- `executeOperatorFind()`
- `executeOperatorTextObj()`
- `executeLineOp()`
- `executeX()`
- `executeReplace()`
- `executeToggleCase()`
- `executeJoin()`
- `executePaste()`
- `executeIndent()`
- `executeOpenLine()`
- `executeOperatorG()`
- `executeOperatorGg()`

**Dependencies:** `../utils/Cursor`, `../utils/intl`, `../utils/stringUtils`, `./textObjects`

**Main flow:** Entry: `executeOperatorMotion()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `vim/textObjects.ts` (186 lines)

**Exports:**
- `TextObjectRange`
- `findTextObject()`

**Dependencies:** `../utils/intl`

**Main flow:** Entry: `findTextObject()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `vim/transitions.ts` (490 lines)

**Exports:**
- `TransitionContext`
- `TransitionResult`
- `transition()`

**Dependencies:** `./motions`

**Main flow:** Entry: `transition()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `vim/types.ts` (199 lines)

**Exports:**
- `Operator`
- `FindType`
- `TextObjScope`
- `VimState`
- `CommandState`
- `PersistentState`
- `RecordedChange`
- `OPERATORS`
- `isOperatorKey()`
- `SIMPLE_MOTIONS`
- `FIND_KEYS`
- `TEXT_OBJ_SCOPES`
- `isTextObjScopeKey()`
- `TEXT_OBJ_TYPES`
- `MAX_VIM_COUNT`
- `createInitialVimState()`
- `createInitialPersistentState()`

**Dependencies:** local only

**Main flow:** Entry: `isOperatorKey()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.


### `voice/voiceModeEnabled.ts` (54 lines)

**Exports:**
- `isVoiceGrowthBookEnabled()`
- `hasVoiceAuth()`
- `isVoiceModeEnabled()`

**Dependencies:** `bun:bundle`, `../services/analytics/growthbook`

**Feature gates:** `VOICE_MODE`

**Main flow:** Entry: `isVoiceGrowthBookEnabled()`

**Boundaries:** Validates inputs at call sites; throws or returns errors per function.

