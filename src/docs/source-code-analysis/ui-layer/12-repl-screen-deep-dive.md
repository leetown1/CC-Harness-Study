# REPL Screen Deep Dive

> File: `src/screens/REPL.tsx` (5,006 lines)
>
> The main REPL screen — renders the entire chat interface, orchestrating message display, user input, session management, UI state transitions, keyboard shortcuts, and the full component tree.

---

## 1. All Imports (Organized by Category)

### Build-time / Dead Code Elimination
```
'bun:bundle'        → feature() for conditional compilation
'child_process'      → spawnSync (for tmux detach in bg sessions)
```

### Bootstrap State
```
'../bootstrap/state.js'
  → snapshotOutputTokensForTurn, getCurrentTurnTokenBudget, getTurnOutputTokens,
    getBudgetContinuationCount, getTotalInputTokens, updateLastInteractionTime,
    getLastInteractionTime, getOriginalCwd, getProjectRoot, getSessionId,
    switchSession, setCostStateForRestore, getTurnHookDurationMs, getTurnHookCount,
    resetTurnHookDuration, getTurnToolDurationMs, getTurnToolCount,
    resetTurnToolDuration, getTurnClassifierDurationMs, getTurnClassifierCount,
    resetTurnClassifierDuration
```

### Utilities
```
'../utils/tokenBudget.js'         → parseTokenBudget
'../utils/array.js'               → count
'path'                            → dirname, join
'os'                              → tmpdir
'figures'                         → unicode glyphs
'../utils/QueryGuard.js'          → QueryGuard (concurrent query guard)
'../utils/envUtils.js'            → isEnvTruthy
'../utils/format.js'              → formatTokens, truncateToWidth
'../utils/earlyInput.js'          → consumeEarlyInput
'../utils/errors.js'              → errorMessage
'../utils/log.js'                 → logError
'../utils/debug.js'               → logForDebugging
'../utils/xml.js'                 → escapeXml
'../utils/thinking.js'            → ThinkingConfig
'../utils/systemPrompt.js'        → buildEffectiveSystemPrompt
'../utils/messages.js'            → textForResubmit, handleMessageFromStream, StreamingToolUse,
                                    StreamingThinking, isCompactBoundaryMessage,
                                    getMessagesAfterCompactBoundary, getContentText,
                                    createUserMessage, createAssistantMessage,
                                    createTurnDurationMessage, createAgentsKilledMessage,
                                    createApiMetricsMessage, createSystemMessage,
                                    createCommandInputMessage, formatCommandInputTags
'../utils/sessionTitle.js'        → generateSessionTitle
'../utils/config.js'              → getGlobalConfig, saveGlobalConfig, getGlobalConfigWriteCount
'../utils/billing.js'             → hasConsoleBillingAccess
'../utils/telemetry/sessionTracing.js' → endInteractionSpan
'../utils/permissions/PermissionUpdate.js' → applyPermissionUpdate, persistPermissionUpdate
'../utils/permissions/filesystem.js' → getScratchpadDir, isScratchpadEnabled
'../utils/permissions/permissionSetup.js' → stripDangerousPermissionsForAutoMode
'../utils/plans.js'               → copyPlanForFork, copyPlanForResume, getPlanSlug, setPlanSlug
'../utils/sessionStorage.js'      → clearSessionMetadata, resetSessionFilePointer,
                                    adoptResumedSessionFile, removeTranscriptMessage,
                                    restoreSessionMetadata, getCurrentSessionTitle,
                                    isEphemeralToolProgress, isLoggableMessage,
                                    saveWorktreeState, getAgentTranscript
'../utils/conversationRecovery.js' → deserializeMessages
'../utils/queryHelpers.js'        → extractReadFilesFromMessages, extractBashToolsFromMessages
'../utils/fileStateCache.js'      → createFileStateCacheWithSizeLimit, mergeFileStateCaches,
                                    READ_FILE_STATE_CACHE_SIZE
'../utils/fileHistory.js'         → fileHistoryMakeSnapshot, FileHistoryState, fileHistoryRewind,
                                    FileHistorySnapshot, copyFileHistoryForResume,
                                    fileHistoryEnabled, fileHistoryHasAnyChanges
'../utils/commitAttribution.js'   → AttributionState, incrementPromptCount
'../utils/sessionRestore.js'      → computeStandaloneAgentContext, restoreAgentFromSession,
                                    restoreSessionStateFromLog, restoreWorktreeForResume,
                                    exitRestoredWorktree
'../utils/concurrentSessions.js'  → isBgSession, updateSessionName, updateSessionActivity
'../utils/permissions/bypassPermissionsKillswitch.js' → checkAndDisableBypassPermissionsIfNeeded,
                                    checkAndDisableAutoModeIfNeeded,
                                    useKickOffCheckAndDisableBypassPermissionsIfNeeded,
                                    useKickOffCheckAndDisableAutoModeIfNeeded
'../utils/toolPool.js'            → mergeAndFilterTools
'../utils/abortController.js'     → createAbortController
'../utils/autoRunIssue.js'        → AutoRunIssueNotification, shouldAutoRunIssue,
                                    getAutoRunIssueReasonText, getAutoRunCommand, AutoRunIssueReason
'../utils/ide.js'                 → IDEExtensionInstallationStatus, closeOpenDiffs,
                                    getConnectedIdeClient, IdeType
'../utils/handlePromptSubmit.js'  → handlePromptSubmit, PromptInputHelpers
'../utils/attachments.js'         → createAttachmentMessage, getQueuedCommandAttachments
'../utils/backgroundHousekeeping.js' → startBackgroundHousekeeping
'../utils/autoUpdater.js'         → AutoUpdaterResult
'../utils/activityManager.js'     → activityManager
'../utils/messageQueueManager.js' → popAllEditable, enqueue, SetAppState, getCommandQueue,
                                    getCommandQueueLength, removeByFilter
'../utils/sandbox/sandbox-adapter.js' → SandboxAskCallback, SandboxManager, NetworkHostPattern
'../utils/queryProfiler.js'       → queryCheckpoint, logQueryProfileReport
'../utils/toolResultStorage.js'   → provisionContentReplacementState,
                                    reconstructContentReplacementState, ContentReplacementRecord
'../utils/promptCategory.js'      → getQuerySourceForREPL
'../utils/gracefulShutdown.js'    → gracefulShutdownSync
'../utils/messagePredicates.js'   → isHumanTurn
'../utils/agentSwarmsEnabled.js'  → isAgentSwarmsEnabled
'../utils/editor.js'              → openFileInExternalEditor
'../utils/exportRenderer.js'      → renderMessagesToPlainText
'../utils/hooks.js'               → executeSessionEndHooks, getSessionEndHookTimeoutMs
'../utils/sessionStart.js'        → processSessionStartHooks
'../utils/claudemd.js'            → getMemoryFiles
'../utils/fullscreen.js'          → isFullscreenEnvEnabled, maybeGetTmuxMouseHint, isMouseTrackingEnabled
'../utils/worktree.js'            → getCurrentWorktreeSession
'../utils/suggestions/shellHistoryCompletion.js' → prependToShellHistoryCache
```

### Swarm / Agent Utilities
```
'../utils/swarm/teamHelpers.js'          → setMemberActive
'../utils/swarm/permissionSync.js'        → isSwarmWorker, generateSandboxRequestId,
                                            sendSandboxPermissionRequestViaMailbox,
                                            sendSandboxPermissionResponseViaMailbox
'../utils/teammate.js'                    → getTeamName, getAgentName
'../utils/swarm/leaderPermissionBridge.js' → registerLeaderToolUseConfirmQueue,
                                            unregisterLeaderToolUseConfirmQueue,
                                            registerLeaderSetToolPermissionContext,
                                            unregisterLeaderSetToolPermissionContext
```

### Ink UI Framework
```
'../ink.js'
  → Box, Text, useStdin, useTheme, useTerminalFocus, useTerminalTitle, useTabStatus, useInput
'../ink/hooks/use-search-highlight.js' → useSearchHighlight
'../ink/terminal.js'                   → hasCursorUpViewportYankBug
'../ink/useTerminalNotification.js'     → useTerminalNotification
'../ink/termio/osc.js'                  → setClipboard
'../ink/components/AlternateScreen.js'  → AlternateScreen
'../ink/components/ScrollBox.js'        → ScrollBoxHandle
'../ink/hooks/use-tab-status.js'        → TabStatusKind
```

### UI Components
```
'../components/CostThresholdDialog.js'
'../components/IdleReturnDialog.js'
'../components/Spinner.js'                    → SpinnerWithVerb, BriefIdleStatus, SpinnerMode
'../components/Messages.js'                   → Messages
'../components/TaskListV2.js'                 → TaskListV2
'../components/TeammateViewHeader.js'
'../components/VirtualMessageList.js'         → JumpHandle
'../components/FullscreenLayout.js'           → FullscreenLayout, useUnseenDivider, computeUnseenDivider
'../components/ScrollKeybindingHandler.js'
'../components/messageActions.js'             → useMessageActions, MessageActionsKeybindings,
                                                MessageActionsBar, MessageActionsState,
                                                MessageActionsNav, MessageActionCaps
'../components/MessageSelector.js'            → MessageSelector, selectableUserMessagesFilter,
                                                messagesAfterAreOnlySynthetic
'../components/PromptInput/PromptInput.js'    → PromptInput
'../components/PromptInput/PromptInputQueuedCommands.js'
'../components/PromptInput/IssueFlagBanner.js' → IssueFlagBanner
'../components/PromptInput/inputModes.js'     → prependModeCharacterToInput
'../components/permissions/PermissionRequest.js' → PermissionRequest, ToolUseConfirm
'../components/permissions/ExitPlanModePermissionRequest/ExitPlanModePermissionRequest.js' → buildPermissionUpdates
'../components/permissions/SandboxPermissionRequest.js'
'../components/permissions/WorkerPendingPermission.js'
'../components/SandboxViolationExpandedView.js'
'../components/mcp/ElicitationDialog.js'
'../components/hooks/PromptDialog.js'
'../components/ExitFlow.js'
'../components/SessionBackgroundHint.js'
'../components/IdeOnboardingDialog.js'
'../components/EffortCallout.js'              → EffortCallout, shouldShowEffortCallout, EffortValue
'../components/RemoteCallout.js'
'../components/AwsAuthStatusBox.js'
'../components/messages/UserTextMessage.js'
'../components/FeedbackSurvey/FeedbackSurvey.js' → FeedbackSurvey
'../components/FeedbackSurvey/useFeedbackSurvey.js' → useFeedbackSurvey
'../components/FeedbackSurvey/useMemorySurvey.js'
'../components/FeedbackSurvey/usePostCompactSurvey.js'
'../components/FeedbackSurvey/useFrustrationDetection.js'
'../components/LspRecommendation/LspRecommendationMenu.js' → LspRecommendationMenu
'../components/ClaudeCodeHint/PluginHintMenu.js' → PluginHintMenu
'../components/DesktopUpsell/DesktopUpsellStartup.js' → DesktopUpsellStartup, shouldShowDesktopUpsellStartup
'../components/AntModelSwitchCallout.js'
'../components/UndercoverAutoCallout.js'
'../components/DevBar.js'
'../components/AutoModeOptInDialog.js'        → AUTO_MODE_DESCRIPTION
'../buddy/CompanionSprite.js'                 → CompanionSprite, CompanionFloatingBubble, MIN_COLS_FOR_FULL_SPRITE
'../components/SkillImprovementSurvey.js'
```

### Hooks
```
'../hooks/useSearchInput.js'
'../hooks/useTerminalSize.js'
'../hooks/useLogMessages.js'
'../hooks/useReplBridge.js'
'../hooks/useIdeLogging.js'
'../hooks/useRemoteSession.js'
'../hooks/useDirectConnect.js'
'../hooks/useSSHSession.js'
'../hooks/useAssistantHistory.js'
'../hooks/useSkillImprovementSurvey.js'
'../hooks/useQueueProcessor.js'
'../hooks/useMailboxBridge.js'
'../hooks/useMergedClients.js'                → mergeClients, useMergedClients
'../hooks/useMergedTools.js'
'../hooks/useMergedCommands.js'
'../hooks/useSkillsChange.js'
'../hooks/useManagePlugins.js'
'../hooks/useTasksV2.js'
'../hooks/useCanUseTool.js'
'../hooks/useApiKeyVerification.js'
'../hooks/useDeferredHookMessages.js'
'../hooks/useAfterFirstRender.js'
'../hooks/useBackgroundTaskNavigation.js'
'../hooks/useSwarmInitialization.js'
'../hooks/useTeammateViewAutoExit.js'
'../hooks/useVoiceIntegration.js'
'../hooks/useMainLoopModel.js'
'../hooks/useIdeSelection.js'                 → IDESelection, useIdeSelection
'../hooks/useIDEIntegration.js'
'../hooks/useCommandQueue.js'
'../hooks/useSessionBackgrounding.js'
'../hooks/useInboxPoller.js'
'../hooks/useSwarmPermissionPoller.js'        → registerSandboxPermissionCallback
'../hooks/useTaskListWatcher.js'
'../hooks/useFileHistorySnapshotInit.js'
'../hooks/useIssueFlagBanner.js'
'../hooks/useLspPluginRecommendation.js'
'../hooks/useClaudeCodeHintRecommendation.js'
'../hooks/useGlobalKeybindings.js'            → GlobalKeybindingHandlers
'../hooks/useCommandKeybindings.js'           → CommandKeybindingHandlers
'../hooks/useCancelRequest.js'                → CancelRequestHandler
'../hooks/useAwaySummary.js'
'../hooks/useChromeExtensionNotification.js'
'../hooks/useOfficialMarketplaceNotification.js'
'../hooks/usePromptsFromClaudeInChrome.js'

// Notification hooks
'../hooks/notifs/useSettingsErrors.js'
'../hooks/notifs/useMcpConnectivityStatus.js'
'../hooks/notifs/useAutoModeUnavailableNotification.js'
'../hooks/notifs/useLspInitializationNotification.js'
'../hooks/notifs/usePluginInstallationStatus.js'
'../hooks/notifs/usePluginAutoupdateNotification.js'
'../hooks/notifs/useRateLimitWarningNotification.js'
'../hooks/notifs/useDeprecationWarningNotification.js'
'../hooks/notifs/useNpmDeprecationNotification.js'
'../hooks/notifs/useIDEStatusIndicator.js'
'../hooks/notifs/useModelMigrationNotifications.js'
'../hooks/notifs/useCanSwitchToExistingSubscription.js'
'../hooks/notifs/useTeammateShutdownNotification.js'
'../hooks/notifs/useFastModeNotification.js'
'../hooks/notifs/useAntOrgWarningNotification.js'
'../hooks/notifs/useInstallMessages.js'
```

### Keybindings
```
'../keybindings/KeybindingProviderSetup.js'   → KeybindingSetup
'../keybindings/useShortcutDisplay.js'        → useShortcutDisplay
'../keybindings/shortcutFormat.js'            → getShortcutDisplay
```

### State
```
'../state/AppState.js' → useAppState, useSetAppState, useAppStateStore
```

### Context
```
'../context.js'               → getSystemContext, getUserContext
'../context/notifications.js' → useNotifications
'../context/fpsMetrics.js'    → useFpsMetrics
```

### Services
```
'src/services/analytics/index.js'       → logEvent, AnalyticsMetadata_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS
'src/services/analytics/growthbook.js'   → getFeatureValue_CACHED_MAY_BE_STALE
'src/services/notifier.js'              → sendNotification
'src/services/preventSleep.js'          → startPreventSleep, stopPreventSleep
'src/services/compact/compact.js'       → partialCompactConversation
'src/services/compact/microCompact.js'  → resetMicrocompactState
'src/services/compact/postCompactCleanup.js' → runPostCompactCleanup
'src/services/diagnosticTracking.js'    → diagnosticTracker
'src/services/PromptSuggestion/speculation.js' → handleSpeculationAccept, ActiveSpeculationState
'src/services/tips/tipScheduler.js'     → getTipToShowOnSpinner, recordShownTip
'src/services/mcp/types.js'             → MCPServerConnection, ScopedMcpServerConfig
'src/services/mcp/MCPConnectionManager.js' → MCPConnectionManager
```

### Constants
```
'../constants/prompts.js'  → getSystemPrompt
'../constants/xml.js'      → BASH_INPUT_TAG, COMMAND_MESSAGE_TAG, COMMAND_NAME_TAG, LOCAL_COMMAND_STDOUT_TAG
```

### Tools
```
'../Tool.js' → ToolPermissionContext, Tool
'../tools.js' → getTools, assembleToolPool
'../tools/BashTool/bashPermissions.js' → clearSpeculativeChecks
'../tools/WebFetchTool/prompt.js' → WEB_FETCH_TOOL_NAME
'../tools/SleepTool/prompt.js' → SLEEP_TOOL_NAME
'../tools/AgentTool/loadAgentsDir.js' → AgentDefinition
'../tools/AgentTool/agentToolUtils.js' → resolveAgentTools
'../tools/AgentTool/resumeAgent.js' → resumeAgentBackground
'../tools/AgentTool/agentColorManager.js' → AgentColorName
'../tools/TungstenTool/TungstenLiveMonitor.js' → TungstenLiveMonitor
'../tools/WebBrowserTool/WebBrowserPanel.js' → WebBrowserPanel
```

### Types
```
'../types/message.js'        → Message, UserMessage, ProgressMessage, HookResultMessage,
                               PartialCompactDirection
'../types/textInputTypes.js' → PromptInputMode, QueuedCommand, VimMode
'../types/ids.js'            → asSessionId, asAgentId
'../types/logs.js'           → LogOption
'../types/hooks.js'          → PromptRequest, PromptResponse, HookProgress
```

### Tasks
```
'../tasks/InProcessTeammateTask/InProcessTeammateTask.js' → injectUserMessageToTeammate,
                                getAllInProcessTeammateTasks
'../tasks/InProcessTeammateTask/types.js' → isInProcessTeammateTask, InProcessTeammateTaskState
'../tasks/LocalAgentTask/LocalAgentTask.js' → isLocalAgentTask, queuePendingMessage,
                                appendMessageToLocalAgent, LocalAgentTaskState
'../tasks/RemoteAgentTask/RemoteAgentTask.js' → restoreRemoteAgentTasks
'../tasks/LocalMainSessionTask.js' → startBackgroundSession
```

### Remote / Bridge
```
'../remote/RemoteSessionManager.js' → RemoteSessionConfig
'../utils/teleport/api.js'          → RemoteMessageContent
```

### Commands / History
```
'../commands.js'     → Command, CommandResultDisplay, ResumeEntrypoint, getCommandName,
                       isCommandEnabled, REMOTE_SAFE_COMMANDS
'../commands/exit/index.js' → exit
'../history.js'     → addToHistory, removeLastFromHistory, expandPastedTextRefs, parseReferences
'../query.js'       → query
```

### Config / Theme
```
'../projectOnboardingState.js' → maybeMarkProjectOnboardingComplete
'../utils/theme.js'            → Theme
'../utils/config.js'           → PastedContent
'../cli/structuredIO.js'       → SANDBOX_NETWORK_ACCESS_TOOL_NAME
'../cost-tracker.js'           → getTotalCost, saveCurrentSessionCosts, resetCostState,
                                 getStoredSessionCosts
'../costHook.js'               → useCostSummary
'../moreright/useMoreRight.js' → useMoreRight
```

### Conditional-Only (Dead Code Eliminated)
```
'../coordinator/coordinatorMode.js'   → getCoordinatorUserContext (COORDINATOR_MODE only)
'../proactive/index.js'               → proactiveModule (PROACTIVE | KAIROS only)
'../proactive/useProactive.js'        → useProactive (PROACTIVE | KAIROS only)
'../hooks/useScheduledTasks.js'       → useScheduledTasks (AGENT_TRIGGERS only)
```

### Sass / Misc
```
'../utils/plugins/performStartupChecks.js'
'../utils/editor.js' → openFileInExternalEditor
'../utils/effort.js' → EffortValue
'fs/promises'        → writeFile
'crypto'             → randomUUID, UUID
'react/compiler-runtime' → c as _c (React Compiler)
```

---

## 2. All Components Defined in This File

### 2.1 `TranscriptModeFooter`
- **Lines:** ~321-362
- **Role:** Footer bar shown at bottom during transcript mode
- **Props:** `showAllInTranscript`, `virtualScroll`, `searchBadge`, `suppressShowAll`, `status`
- **JSX:** Horizontal Box with dimmed Text showing shortcuts and optionally search badge or status
- **Uses React Compiler memoization** (`_c(9)`)

### 2.2 `TranscriptSearchBar`
- **Lines:** ~368-471
- **Role:** less-style `/` search bar for transcript mode
- **Props:** `jumpRef`, `count`, `current`, `onClose`, `onCancel`, `setHighlight`, `initialQuery`
- **Internal State:**
  - `query`, `cursorOffset` (from `useSearchInput`)
  - `indexStatus` - 'building' | { ms } | null
- **Effects:** Warms search index, sets search query on warm completion
- **JSX:** Single-line bar with `/` prompt, query text with inverse cursor, match counter, indexing status

### 2.3 `AnimatedTerminalTitle`
- **Lines:** ~484-519
- **Role:** Sets terminal tab title with animated prefix while query is running
- **Props:** `isAnimating`, `title`, `disabled`, `noPrefix`
- **State:** `frame` - animation frame index
- **Effect:** Sets interval for frame animation when conditions met
- **Returns:** null (side-effect only component)
- **Design rationale:** Isolated from REPL so 960ms tick only re-renders this leaf, not entire REPL

### 2.4 `REPL` (main component / default export)
- **Lines:** ~572-5005
- **Type signature:** `export function REPL({...}: Props): React.ReactNode`
- **Massive orchestration component** — see dedicated sections below

---

## 3. REPL Component: State Variables & Ref Inventory

### 3.1 useState Variables (~40+ states)

| Variable | Type | Purpose |
|---|---|---|
| `mainThreadAgentDefinition` | AgentDefinition \| undefined | Main thread agent (can change via /resume) |
| `localCommands` | Command[] | Hot-reloadable commands (skill file changes) |
| `dynamicMcpConfig` | Record<string,ScopedMcpServerConfig> \| undefined | Dynamic MCP config |
| `screen` | 'prompt' \| 'transcript' | Current screen mode |
| `showAllInTranscript` | boolean | Expand all messages in transcript |
| `dumpMode` | boolean | Dump-to-scrollback mode |
| `editorStatus` | string | v-for-editor render progress |
| `ideSelection` | IDESelection \| undefined | IDE selection state |
| `ideToInstallExtension` | IdeType \| null | IDE for extension install |
| `ideInstallationStatus` | IDEExtensionInstallationStatus \| null | IDE extension install status |
| `showIdeOnboarding` | boolean | Show IDE onboarding dialog |
| `showModelSwitchCallout` | boolean | Ant-only model switch callout |
| `showEffortCallout` | boolean | Effort callout visibility |
| `showDesktopUpsellStartup` | boolean | Desktop upsell dialog |
| `streamMode` | SpinnerMode | 'responding' \| etc. |
| `streamingToolUses` | StreamingToolUse[] | Active streaming tool uses |
| `streamingThinking` | StreamingThinking \| null | Active streaming thinking block |
| `abortController` | AbortController \| null | Current abort controller |
| `isExternalLoading` | boolean | Loading from remote/backgrounding |
| `userInputOnProcessing` | string \| undefined | Placeholder text during processing |
| `autoUpdaterResult` | AutoUpdaterResult \| null | Auto-updater notifications |
| `showUndercoverCallout` | boolean | Undercover auto-enable explainer |
| `toolJSX` | {jsx, shouldHidePromptInput, ...} \| null | Active tool JSX overlay |
| `toolUseConfirmQueue` | ToolUseConfirm[] | Permission request queue |
| `permissionStickyFooter` | ReactNode \| null | Sticky permission footer |
| `sandboxPermissionRequestQueue` | Array<{hostPattern, resolvePromise}> | Sandbox permission queue |
| `promptQueue` | Array<{request, title, resolve, reject}> | Hook prompt queue |
| `messages` | MessageType[] | All conversation messages |
| `cursor` | MessageActionsState \| null | Message actions cursor state |
| `frozenTranscriptState` | {messagesLength, streamingToolUsesLength} \| null | Frozen state for transcript |
| `inputValue` | string | Current prompt input value |
| `inputMode` | PromptInputMode | 'prompt' \| 'bash' etc. |
| `stashedPrompt` | {text, cursorOffset, pastedContents} \| undefined | Stashed prompt for local-jsx |
| `inProgressToolUseIDs` | Set<string> | Track in-progress tool_use IDs |
| `pastedContents` | Record<number, PastedContent> | Pasted content registry |
| `submitCount` | number | Submission counter |
| `streamingText` | string \| null | Streaming text preview |
| `lastQueryCompletionTime` | number | Timestamp of last query completion |
| `spinnerMessage/Color/ShimmerColor` | string \| null / keyof Theme \| null | Spinner customization |
| `isMessageSelectorVisible` | boolean | Message selector modal |
| `messageSelectorPreselect` | UserMessage \| undefined | Pre-selected message for selector |
| `showCostDialog` | boolean | Cost threshold dialog |
| `conversationId` | UUID | Conversation ID (bumped on compact/resume) |
| `idleReturnPending` | {input, idleMinutes} \| null | Idle return dialog state |
| `contentReplacementStateRef` | ref via useState | Content replacement state |
| `haveShownCostDialog` | boolean | Cost dialog shown flag |
| `vimMode` | VimMode | 'INSERT' \| etc. |
| `showBashesDialog` | string \| boolean | Background tasks dialog |
| `isSearchingHistory` | boolean | History search mode |
| `isHelpOpen` | boolean | Help dialog open |
| `autoRunIssueReason` | AutoRunIssueReason \| null | Auto-run /issue reason |
| `exitFlow` | ReactNode \| null | Exit flow component |
| `isExiting` | boolean | Exiting state |
| `remountKey` | number | Remount key for suspend/resume |
| `searchOpen` | boolean | Transcript search bar open |
| `searchQuery` | string | Transcript search query |
| `searchCount/searchCurrent` | number | Search result counts |

### 3.2 useRef Variables (~40+ refs)

| Ref | Type | Purpose |
|---|---|---|
| `editorGenRef` | number | Editor generation counter (stale guard) |
| `editorTimerRef` | ReturnType | Editor status clear timer |
| `editorRenderingRef` | boolean | Editor rendering guard |
| `scrollRef` | ScrollBoxHandle | Fullscreen layout scroll box |
| `modalScrollRef` | ScrollBoxHandle | Modal slot's inner ScrollBox |
| `lastUserScrollTsRef` | number | Last user scroll timestamp |
| `queryGuard` | QueryGuard | Query lifecycle state machine |
| `streamModeRef` | ref mirror | Sync streamMode for callbacks |
| `abortControllerRef` | ref mirror | Sync abortController |
| `sendBridgeResultRef` | () => void | Bridge result callback |
| `restoreMessageSyncRef` | (UserMessage) => void | Sync restore callback |
| `messagesRef` | ref mirror | Sync messages for callbacks |
| `inputValueRef` | ref mirror | Sync input value |
| `userInputBaselineRef` | number | Baseline message count for placeholder |
| `userMessagePendingRef` | boolean | Pending user message flag |
| `wasQueryActiveRef` | boolean | Query active edge detection |
| `loadStartTimeRef` | number | Loading start wall-clock |
| `totalPausedMsRef` | number | Accumulated paused time |
| `pauseStartTimeRef` | number \| null | Pause start timestamp |
| `responseLengthRef` | number | Response character count (for spinner) |
| `apiMetricsRef` | Array | API performance metrics |
| `tipPickedThisTurnRef` | boolean | Tip dedup guard |
| `readFileState` | LRU cache | File read state with size limit |
| `bashTools` | Set<string> | Track bash tools used |
| `bashToolsProcessedIdx` | number | Processed message index |
| `discoveredSkillNamesRef` | Set<string> | Session skill discovery tracking |
| `loadedNestedMemoryPathsRef` | Set<string> | CLAUDE.md dedup |
| `localJSXCommandRef` | object | Persist local JSX across tool updates |
| `sandboxBridgeCleanupRef` | Map<string, Array> | Bridge cleanup functions |
| `hasInterruptibleToolInProgressRef` | boolean | Interruptible tool flag |
| `haikuTitleAttemptedRef` | boolean | One-shot guard for Haiku title |
| `idleHintShownRef` | string \| false | Willow mode variant tracking |
| `cursorNavRef` | MessageActionsNav \| null | Message actions nav |
| `initialMessageRef` | boolean | Initial message processing guard |
| `didAutoRunIssueRef` | boolean | Auto-run issue suppression |
| `safeYoloMessageShownRef` | boolean | Auto-mode warning dedup |
| `worktreeTipShownRef` | boolean | Worktree sparse-checkout tip dedup |
| `hasCountedQueueUseRef` | boolean | Queue usage analytics dedup |
| `onSubmitRef` | ref mirror | Stable onSubmit for MessageRow |
| `jumpRef` | JumpHandle \| null | Virtual message list jump handle |
| `swarmStartTimeRef` | number \| null | Swarm turn start time |
| `swarmBudgetInfoRef` | BudgetInfo \| undefined | Swarm budget info |
| `focusedInputDialogRef` | ref mirror | Sync focusedInputDialog for timers |
| `terminalFocusRef` | ref mirror | Sync terminal focus |
| `prevDialogRef` | ref mirror | Previous dialog for scroll re-pin |
| `prevColsRef` | number | Previous terminal columns for resize |

### 3.3 AppState Selectors (via useAppState)

```
toolPermissionContext, verbose, mcp, plugins, agentDefinitions, fileHistory,
initialMessage, spinnerTip, showExpandedTodos, pendingWorkerRequest,
pendingSandboxRequest, teamContext, tasks, workerSandboxPermissions,
elicitation, ultraplanPendingChoice, ultraplanLaunchPending,
viewingAgentTaskId, isBriefOnly, terminalTitleFromRename, sessionTitle,
showRemoteCallout, reducedMotion, mainLoopModel
```

---

## 4. Keybindings & Input Handlers

### 4.1 Global Keybindings (via `GlobalKeybindingHandlers`)
Rendered inside `<KeybindingSetup>`, receives `globalKeybindingProps`:
```
- screen toggle (ctrl+o) → transcript mode
- showAllInTranscript toggle (ctrl+e)
- Enter/exit transcript callbacks
- Search bar open state
```

### 4.2 Scroll Keybindings (via `ScrollKeybindingHandler`)
- **j/k**: Scroll down/up
- **g/G**: Top/bottom
- **ctrl+u/ctrl+d**: Page up/down
- **PgUp/PgDn**: Page up/down
- **Home/End**: Top/bottom
- **Wheel**: Scroll
- **Drag**: Scroll (mouse)
- Active during normal mode and transcript mode (when not in search bar)

### 4.3 Cancel/Interrupt Handler (via `CancelRequestHandler`)
- **Escape / Ctrl+C**: Cancel active query or dismiss dialog
- Double-press for exit flow
- Props include: `setToolUseConfirmQueue`, `onCancel`, `onAgentsKilled`, `isMessageSelectorVisible`, `screen`, `abortSignal`, `popCommandFromQueue`, `vimMode`, `isLocalJSXCommand`, `isSearchingHistory`, `isHelpOpen`, `inputMode`, `inputValue`, `streamMode`

### 4.4 Voice Keybinding (conditional, VOICE_MODE builds only)
- via `VoiceKeybindingHandler`

### 4.5 Command Keybindings (via `CommandKeybindingHandlers`)
- Triggers slash commands via keybindings
- Passes `onSubmit` with `fromKeybinding: true`

### 4.6 Message Actions Keybindings (via `MessageActionsKeybindings`)
- Conditional on `MESSAGE_ACTIONS` feature and fullscreen
- Active only when `cursor !== null`

### 4.7 useInput Handlers

#### 4.7.1 Transcript Search (line ~4212)
```typescript
useInput((input, key, event) => {
    // '/' → open search bar
    // 'n' → next match (repeated input steps)
    // 'N' → previous match (repeated input steps)
}, {
    isActive: screen === 'transcript' && virtualScrollActive && !searchOpen && !dumpMode
})
```

#### 4.7.2 Transcript Escape Hatches (line ~4270)
```typescript
useInput((input, key, event) => {
    // 'q' → quit transcript (same as ctrl+o toggle)
    // '[' → dump-to-scrollback mode
    // 'v' → open transcript in $VISUAL/$EDITOR
}, {
    isActive: screen === 'transcript' && virtualScrollActive && !searchOpen
})
```

### 4.8 Background Task Navigation Hook
```typescript
useBackgroundTaskNavigation({ onOpenBackgroundTasks: ... })
// Shift+Down → open background tasks dialog
```

---

## 5. State Transitions & The UI State Machine

### 5.1 Query Lifecycle (QueryGuard)

```
                    ┌──────────────┐
                    │    IDLE      │ ← queryGuard.isActive = false
                    └──────┬───────┘
                           │ onSubmit → queryGuard.reserve()
                           ▼
                    ┌──────────────┐
                    │ DISPATCHING  │ ← pre-process (batch input into queue)
                    └──────┬───────┘
                           │ executeUserInput → queryGuard.tryStart()
                           ▼
                    ┌──────────────┐
                    │   RUNNING    │ ← isQueryActive = true
                    └──────┬───────┘
                           │ onQueryImpl → query()
                           │ onQueryEvent → handleMessageFromStream
                           │
                    ┌──────┴───────┐
                    │              │
               success         cancel
                    │              │
                    ▼              ▼
              queryGuard       queryGuard
              .end()           .forceEnd()
                    │              │
                    └──────┬───────┘
                           ▼
                    ┌──────────────┐
                    │    IDLE      │
                    └──────────────┘
```

### 5.2 Screen State

```
         ┌────────────┐     ctrl+o     ┌────────────┐
         │   PROMPT   │ ←───────────→ │ TRANSCRIPT │
         │  (screen=  │               │  (screen=  │
         │  'prompt') │               │ 'transcript│
         └────────────┘               └────────────┘
             │                              │
             │                              │
       showAllInTranscript            showAllInTranscript
            ctrl+e                          ctrl+e
             │                              │
       ┌─────▼──────┐               ┌──────▼───────┐
       │  collapsed  │               │   expanded   │
       │  (30 cap)   │               │  (all msgs)  │
       └────────────┘               └──────────────┘
```

### 5.3 Loading/Spinner State
```
isLoading = isQueryActive || isExternalLoading

showSpinner = isLoading || userInputOnProcessing || hasRunningTeammates || queueLength > 0
  && !pendingWorkerRequest
  && !onlySleepToolActive
  && (!visibleStreamingText || isBriefOnly)
```

### 5.4 Dialog Priority Order (getFocusedInputDialog)

```
1. message-selector           (always highest)
2. sandbox-permission         (suppressed while typing)
3. tool-permission            (only when !toolJSX or shouldContinueAnimation)
4. prompt                     (only when !toolJSX or shouldContinueAnimation)
5. worker-sandbox-permission (only when !toolJSX or shouldContinueAnimation)
6. elicitation               (only when !toolJSX or shouldContinueAnimation)
7. cost                      (only when !toolJSX or shouldContinueAnimation)
8. idle-return               (only when !toolJSX or shouldContinueAnimation)
9. ultraplan-choice          (only when !toolJSX or shouldContinueAnimation, !isLoading)
10. ultraplan-launch          (only when !toolJSX or shouldContinueAnimation, !isLoading)
11. ide-onboarding            (only when !toolJSX or shouldContinueAnimation)
12. model-switch              (ant-only)
13. undercover-callout        (ant-only)
14. effort-callout
15. remote-callout
16. lsp-recommendation
17. plugin-hint
18. desktop-upsell
```

### 5.5 Session Status
```
sessionStatus =
  waiting: isWaitingForApproval || isShowingLocalJSXCommand
  busy:    isLoading
  idle:    otherwise
```

---

## 6. Conditional Rendering Paths

### 6.1 Major Branches

```
REPL
├── screen === 'transcript'
│   ├── Virtual scroll enabled AND !dumpMode
│   │   └── <AlternateScreen>
│   │       └── FullscreenLayout (with ScrollBox)
│   │           ├── Messages (virtual scroll)
│   │           ├── toolJSX
│   │           ├── SandboxViolationExpandedView
│   │           └── TranscriptSearchBar | TranscriptModeFooter
│   ├── !Virtual scroll OR dumpMode
│   │   └── No AlternateScreen, no ScrollBox
│   │       ├── Messages (30-cap)
│   │       ├── toolJSX
│   │       ├── SandboxViolationExpandedView
│   │       └── TranscriptModeFooter
│   └── KeybindingSetup wrapping everything
│
└── screen === 'prompt' (main return)
    ├── isFullscreenEnvEnabled()
    │   └── <AlternateScreen>
    │       └── KeybindingSetup
    │           └── MCPConnectionManager
    │               └── FullscreenLayout
    └── !isFullscreenEnvEnabled()
        └── KeybindingSetup
            └── MCPConnectionManager
                └── FullscreenLayout (passthrough)
```

### 6.2 Remote Modes
- **useRemoteSession**: `claude --ccr` — WebSocket to CCR
- **useDirectConnect**: `claude connect` — WebSocket to claude server
- **useSSHSession**: `claude ssh` — SSH transport
- Priority: sshRemote > directConnect > remoteSession

### 6.3 Remote vs Local Rendering Differences
- Remote mode: messages sent via WebSocket, local-jsx commands execute locally
- `isExternalLoading` gates spinner for remote queries
- Remote mode skips `handlePromptSubmit`, routes directly to `activeRemote.sendMessage()`

### 6.4 Fullscreen vs Non-Fullscreen
- Fullscreen: `<AlternateScreen>`, `<ScrollBox>`, virtual scroll, sticky prompt pill
- Non-Fullscreen: terminal scrollback, message cap, no modal pane, no pill

### 6.5 Teammate/Agent Viewing
- When `viewingAgentTaskId` is set:
  - Messages switch from main conversation to agent's messages
  - `TeammateViewHeader` renders
  - `onAgentSubmit` handles input (sends to teammate instead of main loop)
  - `hidePill` and `hideSticky` pass to FullscreenLayout
  - UnseenDivider hidden
  - isBriefOnly overridden to false

---

## 7. Message Rendering Pipeline

### 7.1 Data Flow
```
messages (useState)
    │
    ├─→ messagesRef.current (sync, always fresh)
    │
    ├─→ deferredMessages = useDeferredValue(messages)
    │   (transition priority, yields every 5ms)
    │
    ├─→ displayedMessages:
    │   │
    │   ├── viewedAgentTask? → agent messages
    │   ├── usesSyncMessages? → messages (synchronous)
    │   │   (showStreamingText || !isLoading)
    │   └── otherwise → deferredMessages
    │
    └─→ <Messages messages={displayedMessages} ... />
```

### 7.2 Streaming Text
```
streamingText (useState)
    │
    ├─→ onStreamingText handler (set by onQueryEvent → handleMessageFromStream)
    │   ├── Reduced motion? → nothing
    │   ├── Cursor viewport bug? → nothing
    │   └── Otherwise → setStreamingText(updater)
    │
    └─→ visibleStreamingText:
        streamingText?.substring(0, lastIndexOf('\n') + 1) || null
        (line-by-line, not char-by-char)
```

### 7.3 onQueryEvent → handleMessageFromStream
```
for await (const event of query(...)) {
    onQueryEvent(event)
        │
        ├── COMPACT BOUNDARY message
        │   ├── Fullscreen: keep pre-compact for scrollback
        │   └── Non-fullscreen: replace all messages
        │   └── Bump conversationId
        │   └── Clear proactive context-blocked
        │
        ├── EPHEMERAL progress (sleep/bash ticks)
        │   └── Replace last matching progress msg (don't append)
        │
        └── REGULAR message
            └── append to messages[]
            └── Update response length ref
            └── Handle API error → block proactive
```

### 7.4 Messages Component Props
```
<Messages
    messages={displayedMessages}
    tools={tools}
    commands={commands}
    verbose={verbose}
    toolJSX={toolJSX}
    toolUseConfirmQueue={toolUseConfirmQueue}
    inProgressToolUseIDs={...}
    isMessageSelectorVisible={isMessageSelectorVisible}
    conversationId={conversationId}
    screen={screen}
    streamingToolUses={streamingToolUses}
    showAllInTranscript={showAllInTranscript}
    agentDefinitions={agentDefinitions}
    onOpenRateLimitOptions={handleOpenRateLimitOptions}
    isLoading={isLoading}
    streamingText={visibleStreamingText}
    isBriefOnly={isBriefOnly}
    unseenDivider={unseenDivider}
    scrollRef={scrollRef}
    trackStickyPrompt={...}
    cursor={cursor}
    setCursor={setCursor}
    cursorNavRef={cursorNavRef}
    // transcript-only:
    jumpRef={jumpRef}
    onSearchMatchesChange={onSearchMatchesChange}
    scanElement={scanElement}
    setPositions={setPositions}
    disableRenderCap={dumpMode}
/>
```

---

## 8. Dialog/Overlay Rendering in `bottom` Slot

All dialogs render in the `<FullscreenLayout bottom={...}>` slot (or inline for non-fullscreen):

```
bottom slot:
├── permissionStickyFooter
├── Immediate local-jsx tool JSX (not centered)
│   └── toolJSX.isLocalJSXCommand && toolJSX.isImmediate && !toolJsxCentered
├── TaskListV2 (showExpandedTodos)
├── SandboxPermissionRequest (focusedInputDialog === 'sandbox-permission')
├── PromptDialog (focusedInputDialog === 'prompt')
├── WorkerPendingPermission (pendingWorkerRequest)
├── WorkerPendingPermission (pendingSandboxRequest)
├── SandboxPermissionRequest (focusedInputDialog === 'worker-sandbox-permission')
├── ElicitationDialog (focusedInputDialog === 'elicitation')
├── CostThresholdDialog (focusedInputDialog === 'cost')
├── IdleReturnDialog (focusedInputDialog === 'idle-return')
├── IdeOnboardingDialog (focusedInputDialog === 'ide-onboarding')
├── AntModelSwitchCallout (focusedInputDialog === 'model-switch')
├── UndercoverAutoCallout (focusedInputDialog === 'undercover-callout')
├── EffortCallout (focusedInputDialog === 'effort-callout')
├── RemoteCallout (focusedInputDialog === 'remote-callout')
├── PluginHintMenu (focusedInputDialog === 'plugin-hint')
├── LspRecommendationMenu (focusedInputDialog === 'lsp-recommendation')
├── DesktopUpsellStartup (focusedInputDialog === 'desktop-upsell')
├── UltraplanChoiceDialog (focusedInputDialog === 'ultraplan-choice')
├── UltraplanLaunchDialog (focusedInputDialog === 'ultraplan-launch')
├── exitFlow
├── mrRender() (MoreRight)
├── PromptInput (when !toolJSX?.shouldHidePromptInput && !focusedInputDialog && !isExiting && !disabled && !cursor)
│   └── with surveys, feedback, skill improvement
├── MessageActionsBar (when cursor !== null)
├── MessageSelector (focusedInputDialog === 'message-selector')
└── DevBar (ant-only)
```

---

## 9. Session Lifecycle

### 9.1 Initialization
```
1. REPL mounts (useEffect → logDebug)
2. onInit() fires:
   a. reverify() API key
   b. getMemoryFiles() → populate readFileState cache
3. processInitialMessage effect:
   - If initialMessage.clearContext → clearConversation()
   - Apply permission mode
   - Make file history snapshot
   - awaitPendingHooks()
   - Route through onSubmit() or onQuery()
```

### 9.2 During Session
```
- User types → inputValue updates → activity tracked
- User submits → onSubmit():
  1. repinScroll()
  2. Resume proactive (if paused)
  3. Check for immediate commands
  4. Idle-return check
  5. Add to history
  6. Handle stash
  7. Set userInputOnProcessing placeholder
  8. handlePromptSubmit() → processUserInput → onQueryImpl → query()
  9. onQueryEvent() processes stream
  10. onTurnComplete callback
```

### 9.3 Session Resume (via /resume)
```
resume(sessionId, log, entrypoint)
├── deserializeMessages()
├── matchSessionMode (coordinator mode)
├── executeSessionEndHooks('resume')
├── processSessionStartHooks('resume')
├── copyPlanForFork/copyPlanForResume
├── restoreSessionStateFromLog
├── restoreAgentFromSession
├── computeStandaloneAgentContext
├── restoreReadFileState
├── resetLoadingState
├── switchSession(sessionId, projectPath)
├── renameRecordingForSession
├── resetSessionFilePointer
├── clearSessionMetadata → restoreSessionMetadata
├── exitRestoredWorktree → restoreWorktreeForResume
├── adoptResumedSessionFile
├── restoreRemoteAgentTasks
├── saveMode (coordinator)
├── setCostStateForRestore
├── reconstructContentReplacementState
├── setMessages(new messages)
├── setConversationId(sessionId)
└── logEvent
```

### 9.4 Session Backgrounding
```
handleBackgroundQuery():
├── abortController?.abort('background')
├── Remove task-notification commands from queue
├── Build system prompt + user/system context
├── startBackgroundSession({messages, queryParams, ...})
└── useSessionBackgrounding handles detach/reattach
```

### 9.5 Cleanup / Exit
```
handleExit():
├── setIsExiting(true)
├── isBgSession? → tmux detach-client → return
├── showWorktree? → setExitFlow(<ExitFlow .../>)
├── Otherwise → exit.call() → graceful shutdown
└── setExitFlow(result)
```

### 9.6 Suspend/Resume
```
internal_eventEmitter:
├── 'suspend' → print instruction
└── 'resume' → setRemountKey(prev+1) → remount MCPConnectionManager
```

---

## 10. Integration Points

### 10.1 Hooks Integration
```
useLogMessages         → Records transcripts to disk
useReplBridge          → Syncs to bridge (claude.ai)
useQueueProcessor      → Processes queued commands
useMailboxBridge       → Swarm inter-process messaging
useInboxPoller         → Polls for teammate messages
useSessionBackgrounding → Background/foreground sessions
useRemoteSession       → CCR WebSocket
useDirectConnect       → Direct connect WebSocket
useSSHSession          → SSH transport
useIDEIntegration      → IDE client management
useCostSummary         → Cost tracking
useFpsMetrics          → Performance monitoring
useAfterFirstRender    → Post-first-render actions
useDeferredHookMessages → Awaits pending hook messages
useApiKeyVerification  → API key validation
useSwarmInitialization  → Teammate hooks and context
useTeammateViewAutoExit → Auto-exit on teammate completion
useFileHistorySnapshotInit → Restore file history
useBackgroundTaskNavigation → Shift+Down shortcuts
useVoiceIntegration    → Voice input (VOICE_MODE)
useAwaySummary         → Auto-summary when away (AWAY_SUMMARY)
useLspPluginRecommendation   → LSP plugin suggestion
useClaudeCodeHintRecommendation → Plugin hint
```

### 10.2 Notification Hooks (render-passive)
```
useModelMigrationNotifications
useCanSwitchToExistingSubscription
useIDEStatusIndicator
useMcpConnectivityStatus
useAutoModeUnavailableNotification
usePluginInstallationStatus
usePluginAutoupdateNotification
useSettingsErrors
useRateLimitWarningNotification
useFastModeNotification
useDeprecationWarningNotification
useNpmDeprecationNotification
useAntOrgWarningNotification
useInstallMessages
useChromeExtensionNotification
useOfficialMarketplaceNotification
useLspInitializationNotification
useTeammateLifecycleNotification
```

### 10.3 Survey / Feedback Integration
```
useFeedbackSurvey         → Main feedback survey
useMemorySurvey           → Memory usage survey
usePostCompactSurvey      → Post-compact survey
useFrustrationDetection   → Frustration-triggered transcript sharing
useSkillImprovementSurvey → Skill improvement (ant-only)
useIssueFlagBanner        → Issue flag prompt
```

### 10.4 Bridge Integration
```
useReplBridge(messages, setMessages, abortControllerRef, commands, mainLoopModel):
  → sendBridgeResult (ref stored in sendBridgeResultRef)
  → sends result on turn completion

Sandbox bridge:
  sandboxAskCallback → forward to bridge (BRIDGE_MODE)
  sandboxBridgeCleanupRef → cancel remote prompts

Leader/Tool bridges:
  registerLeaderToolUseConfirmQueue
  registerLeaderSetToolPermissionContext
  registerSandboxPermissionCallback
```

### 10.5 Tool/Agent Integration
```
canUseTool → permission checks
resolveAgentTools → filter tools for agent
getToolUseContext() → build context for query:
  - assembleToolPool/mergeAndFilterTools
  - mergeClients (MCP)
  - refreshTools callback
  - refreshable from store at call time
```

### 10.6 Proactive/Loop Mode Integration (ant-only)
```
useProactive({
    isLoading, queuedCommandsLength, hasActiveLocalJsxUI,
    isInPlanMode, onSubmitTick, onQueueTick
})

useTaskListWatcher({ taskListId, isLoading, onSubmitTask })
useScheduledTasks({ isLoading, assistantMode, setMessages })

proactiveModule:
  - setContextBlocked(true/false) → on API errors
  - isProactiveActive() → user context adjustment
  - pauseProactive/resumeProactive → on cancel/submit
```

---

## 11. Key Architectural Patterns

### 11.1 Ref-Mirror Pattern
State variables that change frequently during streaming are mirrored in refs to keep callback closures stable:
```
streamModeRef.current = streamMode
abortControllerRef.current = abortController
messagesRef.current = messages (with custom setter)
inputValueRef.current = inputValue
onSubmitRef.current = onSubmit (prevents REPL scope pinning)
```

### 11.2 QueryGuard State Machine
Single atomic guard replaces the old dual-state (isLoading + isQueryRunning):
```
queryGuard.reserve() → dispatching
queryGuard.tryStart() → running (returns generation number, null if busy)
queryGuard.end(gen) → idle (checks generation, false if stale)
queryGuard.forceEnd() → idle (bypasses generation check)
queryGuard.isActive → derived from state
```

### 11.3 Custom setMessages Wrapper
```
setMessages(action) {
    1. Compute new messages (functional updater support)
    2. Update messagesRef immediately (sync)
    3. Handle userInputBaseline for placeholder
    4. rawSetMessages(next) (React state)
}
```

### 11.4 Fresh-from-Store State
`getToolUseContext` and `onQueryImpl` read mutable values from `store.getState()` at call time rather than closure-captured snapshots:
- `computeTools()` reads latest MCP tools
- `mergeClients()` reads latest MCP clients
- Avoids stale closures between render and async gap

### 11.5 Scroll/Auto-pin Logic
```
Submit → repinScroll() (scrollToBottom + onRepin + clear cursor)
Last message is human turn → repinScroll effect
Typing into empty input → repinScroll (unless scrolled <3s ago)
Permission overlay appear/dismiss → repinScroll (useLayoutEffect)
```

### 11.6 Deferred Messages (useDeferredValue)
```
messages → deferredMessages (transition priority, 5ms yield)
Displayed path:
  - showing streaming text → sync (no defer)
  - not loading → sync (no defer)
  - reduced motion + loading → deferred
  - viewing agent → agent messages (no defer)
```

---

## 12. onQueryImpl - The Core Query Pipeline

```
onQueryImpl(messagesInclNew, newMessages, abortController, shouldQuery, additionalTools, model, effort)
├── diagnosticTracker.handleQueryStart
├── closeOpenDiffs (if IDE connected)
├── maybeMarkProjectOnboardingComplete
├── generateSessionTitle (Haiku, one-shot)
├── Apply slash-command allowedTools to store
├── !shouldQuery → resetLoadingState, return
├── getToolUseContext() (fresh from store)
├── If effort override: wrap getAppState
├── Promise.all:
│   ├── checkAndDisableBypassPermissionsIfNeeded
│   ├── checkAndDisableAutoModeIfNeeded (if classifier)
│   ├── getSystemPrompt(tools, model, dirs, mcp)
│   ├── getUserContext()
│   └── getSystemContext()
├── userContext += coordinator/proactive adjustments
├── buildEffectiveSystemPrompt
├── resetTurnHookDuration/ToolDuration/ClassifierDuration
├── for await (const event of query({...}))
│   └── onQueryEvent(event)
├── fireCompanionObserver (BUDDY)
├── Ant-only API metrics → createApiMetricsMessage
├── resetLoadingState
├── logQueryProfileReport
└── onTurnComplete?.(messagesRef.current)
```

---

## 13. ToolJSX Overlay Management

### 13.1 setToolJSX Wrapper
```
setToolJSX(args):
├── isLocalJSXCommand → store in localJSXCommandRef, set overlay
├── clearLocalJSX → clear ref + overlay
├── localJSXCommandRef.current active → ignore (keep local overlay)
└── otherwise → set overlay normally
```

### 13.2 Rendering Locations
```
toolJSX renders in:
  1. scrollable slot (non-immediate, non-local-jsx)
  2. bottom slot (immediate local-jsx, non-centered)
  3. modal slot (centered, fullscreen, FullscreenLayout)
```

### 13.3 Immediate Command Flow
```
/immediateCommand typed → onSubmit:
  1. Check matchingCommand?.immediate
  2. Execute command directly (bypasses queue)
  3. command.load() → command.call(onDone, context, args)
  4. onDone:
     - setToolJSX({clearLocalJSX: true})
     - Add notifications
     - Append meta/new messages
     - Restore stashed prompt
  5. Return early (no history add, no queue)
```

---

## 14. Performance Optimizations

1. **Ref mirrors** prevent callback recreation (~30×/turn)
2. **useDeferredValue** keeps input responsive during message processing
3. **getToolUseContext reads from store** not closure-captured state
4. **useCallback with careful deps** — onSubmit uses messagesRef not messages
5. **React Compiler** memoizes TranscriptModeFooter, AnimatedTerminalTitle, TranscriptSearchBar
6. **Ephemeral progress dedup** — replace instead of append sleep/bash ticks
7. **Scroll refs not state** — per-frame scroll never re-renders REPL
8. **Empty array constants** (EMPTY_MCP_CLIENTS) stop unnecessary effect fires
9. **AnimatedTerminalTitle isolation** — 960ms tick renders only that leaf
10. **onSubmitRef** prevents MessageRow fibers from pinning old REPL scopes

---

## 15. Error & Edge Case Handling

1. **Concurrent query guard** — QueryGuard prevents overlapping queries; enqueues duplicates
2. **Auto-restore on interrupt** — If user cancels before meaningful response, rewind
3. **Stale editor generation** — editorGenRef prevents late writes from async render
4. **Double-tap prevention** — editorRenderingRef blocks parallel v-for-editor renders
5. **Sandbox unavailable** — Graceful shutdown if sandbox required but unavailable
6. **Cost threshold** — Shown once per session when $5 reached, if console billing access
7. **API error → context blocked** — Prevents proactive tick error loops
8. **willow_mode idle return** — dialog/hint/hint_v2 for long-idle sessions
9. **Fullscreen scrollRef reuse** — transcript and normal modes share ref, only one ScrollBox mounted
10. **Worktree sparse-checkout tip** — shown once if creation >15s without sparse paths
