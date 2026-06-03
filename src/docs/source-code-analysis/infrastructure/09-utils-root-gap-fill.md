# 09 — Utils Root Gap Fill

> **Scope**: 267 root-level `utils/*.ts` files not given dedicated sections in `07-utils-layer.md` §15.
> **Verified**: 23 files already documented in §15 (auth, config, log, debug, errors, file, path, etc.).
> **Generated**: Phase 1 audit (Agent A9) — exports and line counts verified against source.

---

# Part 1 — Root-Level Files (267 entries)

## `utils/abortController.ts` (99 lines)

**Exports:**
- `createAbortController`
- `createChildAbortController`

**Dependencies:** local only

**Main flow:** Entry: `createAbortController()`

**Behavior:** Nested AbortController helper for propagating cancellation through async trees.

## `utils/activityManager.ts` (164 lines)

**Exports:**
- `ActivityManager`
- `activityManager`

**Dependencies:** `../bootstrap/state.js`

**Main flow:** Entry: `ActivityManager()`

**Behavior:** Tracks in-flight tool/assistant activities for status UI and bridge worker sync.

## `utils/advisor.ts` (145 lines)

**Exports:**
- `ADVISOR_TOOL_INSTRUCTIONS`
- `AdvisorBlock`
- `AdvisorServerToolUseBlock`
- `AdvisorToolResultBlock`
- `canUserConfigureAdvisor`
- `getAdvisorUsage`
- `getExperimentAdvisorModels`
- `getInitialAdvisorSetting`
- `isAdvisorBlock`
- `isAdvisorEnabled`
- `isValidAdvisorModel`
- `modelSupportsAdvisor`

**Dependencies:** `../services/analytics/growthbook.js`, `./betas.js`, `./envUtils.js`, `./settings/settings.js`

**Main flow:** Entry: `isAdvisorBlock()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/agentContext.ts` (178 lines)

**Exports:**
- `AgentContext`
- `SubagentContext`
- `TeammateAgentContext`
- `consumeInvokingRequestId`
- `getAgentContext`
- `getSubagentLogName`
- `isSubagentContext`
- `isTeammateAgentContext`
- `runWithAgentContext`

**Dependencies:** `../services/analytics/index.js`, `./agentSwarmsEnabled.js`

**Main flow:** Entry: `isSubagentContext()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/agenticSessionSearch.ts` (307 lines)

**Exports:**
- `agenticSessionSearch`

**Dependencies:** `../types/logs.js`, `./array.js`, `./debug.js`, `./log.js`, `./model/model.js`, `./sessionStorage.js`, `./sideQuery.js`, `./slowOperations.js`

**Main flow:** Entry: `agenticSessionSearch()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/agentId.ts` (99 lines)

**Exports:**
- `formatAgentId`
- `generateRequestId`
- `parseAgentId`
- `parseRequestId`

**Dependencies:** local only

**Main flow:** Entry: `parseAgentId()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/agentSwarmsEnabled.ts` (44 lines)

**Exports:**
- `isAgentSwarmsEnabled`

**Dependencies:** `../services/analytics/growthbook.js`, `./envUtils.js`

**Main flow:** Entry: `isAgentSwarmsEnabled()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/analyzeContext.ts` (1382 lines)

**Exports:**
- `ContextData`
- `DeferredBuiltinTool`
- `SystemPromptSectionDetail`
- `SystemToolDetail`
- `TOOL_TOKEN_COUNT_OVERHEAD`
- `analyzeContextUsage`
- `countMcpToolTokens`
- `countToolDefinitionTokens`

**Dependencies:** `../Tool.js`, `../bootstrap/state.js`, `../commands.js`, `../context.js`, `../services/analytics/growthbook.js`, `../services/compact/autoCompact.js`, `../services/tokenEstimation.js`, `../skills/loadSkillsDir.js`, `../tools/AgentTool/loadAgentsDir.js`, `../tools/SkillTool/constants.js`

**Feature gates:** `CONTEXT_COLLAPSE`, `REACTIVE_COMPACT`

**Main flow:** Entry: `ContextData()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/ansiToPng.ts` (334 lines)

**Exports:**
- `AnsiToPngOptions`
- `ansiToPng`

**Dependencies:** `../ink/stringWidth.js`, `./ansiToSvg.js`

**Main flow:** Entry: `AnsiToPngOptions()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/ansiToSvg.ts` (272 lines)

**Exports:**
- `AnsiColor`
- `AnsiToSvgOptions`
- `DEFAULT_BG`
- `DEFAULT_FG`
- `ParsedLine`
- `TextSpan`
- `ansiToSvg`
- `parseAnsi`

**Dependencies:** `./xml.js`

**Main flow:** Entry: `parseAnsi()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/api.ts` (718 lines)

**Exports:**
- `CacheScope`
- `SystemPromptBlock`
- `appendSystemContext`
- `logAPIPrefix`
- `logContextMetrics`
- `normalizeToolInput`
- `normalizeToolInputForAPI`
- `prependUserContext`
- `splitSysPromptPrefix`
- `toolToAPISchema`

**Dependencies:** `../Tool.js`, `../constants/system.js`, `../services/tokenEstimation.js`, `../tools/AgentTool/constants.js`, `../tools/AgentTool/loadAgentsDir.js`, `../tools/ExitPlanModeTool/constants.js`, `../tools/TaskOutputTool/constants.js`, `../types/message.js`, `./agentSwarmsEnabled.js`, `./betas.js`

**Main flow:** Entry: `CacheScope()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/apiPreconnect.ts` (71 lines)

**Exports:**
- `preconnectAnthropicApi`

**Dependencies:** `../constants/oauth.js`, `./envUtils.js`

**Main flow:** Entry: `preconnectAnthropicApi()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/appleTerminalBackup.ts` (124 lines)

**Exports:**
- `backupTerminalPreferences`
- `checkAndRestoreTerminalBackup`
- `getTerminalPlistPath`
- `markTerminalSetupComplete`
- `markTerminalSetupInProgress`

**Dependencies:** `./config.js`, `./execFileNoThrow.js`, `./log.js`

**Main flow:** Entry: `getTerminalPlistPath()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/argumentSubstitution.ts` (145 lines)

**Exports:**
- `generateProgressiveArgumentHint`
- `parseArgumentNames`
- `parseArguments`
- `substituteArguments`

**Dependencies:** `./bash/shellQuote.js`

**Main flow:** Entry: `parseArgumentNames()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/asciicast.ts` (239 lines)

**Exports:**
- `_resetRecordingStateForTesting`
- `flushAsciicastRecorder`
- `getRecordFilePath`
- `getSessionRecordingPaths`
- `installAsciicastRecorder`
- `renameRecordingForSession`

**Dependencies:** `../bootstrap/state.js`, `./bufferedWriter.js`, `./cleanupRegistry.js`, `./debug.js`, `./envUtils.js`, `./fsOperations.js`, `./path.js`, `./slowOperations.js`

**Main flow:** Entry: `getRecordFilePath()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/attribution.ts` (393 lines)

**Exports:**
- `AttributionTexts`
- `countUserPromptsInMessages`
- `getAttributionTexts`
- `getEnhancedPRAttribution`

**Dependencies:** `../bootstrap/state.js`, `../constants/product.js`, `../constants/xml.js`, `../state/AppState.js`, `../tools/FileEditTool/constants.js`, `../tools/FileReadTool/prompt.js`, `../tools/FileWriteTool/prompt.js`, `../tools/GlobTool/prompt.js`, `../tools/GrepTool/prompt.js`, `../types/logs.js`

**Feature gates:** `COMMIT_ATTRIBUTION`

**Main flow:** Entry: `getAttributionTexts()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/authFileDescriptor.ts` (196 lines)

**Exports:**
- `CCR_API_KEY_PATH`
- `CCR_OAUTH_TOKEN_PATH`
- `CCR_SESSION_INGRESS_TOKEN_PATH`
- `getApiKeyFromFileDescriptor`
- `getOAuthTokenFromFileDescriptor`
- `maybePersistTokenForSubprocesses`
- `readTokenFromWellKnownFile`

**Dependencies:** `../bootstrap/state.js`, `./debug.js`, `./envUtils.js`, `./errors.js`, `./fsOperations.js`

**Main flow:** Entry: `getApiKeyFromFileDescriptor()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/authPortable.ts` (19 lines)

**Exports:**
- `maybeRemoveApiKeyFromMacOSKeychainThrows`
- `normalizeApiKeyForConfig`

**Dependencies:** local only

**Main flow:** Entry: `maybeRemoveApiKeyFromMacOSKeychainThrows()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/autoModeDenials.ts` (26 lines)

**Exports:**
- `AutoModeDenial`
- `getAutoModeDenials`
- `recordAutoModeDenial`

**Dependencies:** local only

**Feature gates:** `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `getAutoModeDenials()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/autoUpdater.ts` (561 lines)

**Exports:**
- `AutoUpdaterResult`
- `InstallStatus`
- `MaxVersionConfig`
- `NpmDistTags`
- `assertMinVersion`
- `checkGlobalInstallPermissions`
- `getGcsDistTags`
- `getLatestVersion`
- `getLatestVersionFromGcs`
- `getLockFilePath`
- `getMaxVersion`
- `getMaxVersionMessage`
- `getNpmDistTags`
- `getVersionHistory`
- `installGlobalPackage`
- `shouldSkipVersion`

**Dependencies:** `./config.js`, `./debug.js`, `./env.js`, `./envUtils.js`, `./errors.js`, `./execFileNoThrow.js`, `./fsOperations.js`, `./gracefulShutdown.js`, `./log.js`, `./semver.js`

**Main flow:** Entry: `getGcsDistTags()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/aws.ts` (74 lines)

**Exports:**
- `AwsCredentials`
- `AwsStsOutput`
- `checkStsCallerIdentity`
- `clearAwsIniCache`
- `isAwsCredentialsProviderError`
- `isValidAwsStsOutput`

**Dependencies:** `./debug.js`

**Main flow:** Entry: `isAwsCredentialsProviderError()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/awsAuthStatusManager.ts` (81 lines)

**Exports:**
- `AwsAuthStatus`
- `AwsAuthStatusManager`

**Dependencies:** `./signal.js`

**Main flow:** Entry: `AwsAuthStatus()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/backgroundHousekeeping.ts` (94 lines)

**Exports:**
- `startBackgroundHousekeeping`

**Dependencies:** `../bootstrap/state.js`, `../services/MagicDocs/magicDocs.js`, `../services/autoDream/autoDream.js`, `./cleanup.js`, `./hooks/skillImprovement.js`, `./nativeInstaller/index.js`, `./plugins/pluginAutoupdate.js`

**Feature gates:** `EXTRACT_MEMORIES`, `LODESTONE`

**Main flow:** Entry: `startBackgroundHousekeeping()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/betas.ts` (434 lines)

**Exports:**
- `clearBetasCaches`
- `filterAllowedSdkBetas`
- `getAllModelBetas`
- `getBedrockExtraBodyParamsBetas`
- `getMergedBetas`
- `getModelBetas`
- `getToolSearchBetaHeader`
- `modelSupportsAutoMode`
- `modelSupportsContextManagement`
- `modelSupportsISP`
- `modelSupportsStructuredOutputs`
- `shouldIncludeFirstPartyOnlyBetas`
- `shouldUseGlobalCacheScope`

**Dependencies:** `../bootstrap/state.js`, `../constants/betas.js`, `../constants/oauth.js`, `./auth.js`, `./context.js`, `./envUtils.js`, `./model/model.js`, `./model/modelSupportOverrides.js`, `./model/providers.js`, `./settings/settings.js`

**Feature gates:** `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `getAllModelBetas()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/billing.ts` (78 lines)

**Exports:**
- `hasClaudeAiBillingAccess`
- `hasConsoleBillingAccess`
- `setMockBillingAccessOverride`

**Dependencies:** `./auth.js`, `./config.js`, `./envUtils.js`

**Main flow:** Entry: `hasClaudeAiBillingAccess()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/binaryCheck.ts` (53 lines)

**Exports:**
- `clearBinaryCache`
- `isBinaryInstalled`

**Dependencies:** `./debug.js`, `./which.js`

**Main flow:** Entry: `isBinaryInstalled()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/browser.ts` (68 lines)

**Exports:**
- `openBrowser`
- `openPath`

**Dependencies:** `./execFileNoThrow.js`

**Main flow:** Entry: `openBrowser()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/bufferedWriter.ts` (100 lines)

**Exports:**
- `BufferedWriter`
- `createBufferedWriter`

**Dependencies:** local only

**Main flow:** Entry: `createBufferedWriter()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/bundledMode.ts` (22 lines)

**Exports:**
- `isInBundledMode`
- `isRunningWithBun`

**Dependencies:** local only

**Main flow:** Entry: `isInBundledMode()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/caCerts.ts` (115 lines)

**Exports:**
- `clearCACertsCache`
- `getCACertificates`

**Dependencies:** `./debug.js`, `./envUtils.js`, `./fsOperations.js`

**Main flow:** Entry: `getCACertificates()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/caCertsConfig.ts` (88 lines)

**Exports:**
- `applyExtraCACertsFromConfig`

**Dependencies:** `./config.js`, `./debug.js`, `./settings/settings.js`

**Main flow:** Entry: `applyExtraCACertsFromConfig()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/cachePaths.ts` (38 lines)

**Exports:**
- `CACHE_PATHS`

**Dependencies:** `./fsOperations.js`, `./hash.js`

**Main flow:** Entry: `CACHE_PATHS()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/CircularBuffer.ts` (84 lines)

**Exports:**
- `CircularBuffer`

**Dependencies:** local only

**Main flow:** Entry: `CircularBuffer()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/classifierApprovals.ts` (88 lines)

**Exports:**
- `clearClassifierApprovals`
- `clearClassifierChecking`
- `deleteClassifierApproval`
- `getClassifierApproval`
- `getYoloClassifierApproval`
- `isClassifierChecking`
- `setClassifierApproval`
- `setClassifierChecking`
- `setYoloClassifierApproval`
- `subscribeClassifierChecking`

**Dependencies:** `./signal.js`

**Feature gates:** `BASH_CLASSIFIER`, `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `isClassifierChecking()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/classifierApprovalsHook.ts` (17 lines)

**Exports:**
- `useIsClassifierChecking`

**Dependencies:** `./classifierApprovals.js`

**Main flow:** Entry: `useIsClassifierChecking()`

**Behavior:** Hook lifecycle helper; registers callbacks or dispatches hook events.

## `utils/claudeCodeHints.ts` (193 lines)

**Exports:**
- `ClaudeCodeHint`
- `ClaudeCodeHintType`
- `_resetClaudeCodeHintStore`
- `_test`
- `clearPendingHint`
- `extractClaudeCodeHints`
- `getPendingHintSnapshot`
- `hasShownHintThisSession`
- `markShownThisSession`
- `setPendingHint`
- `subscribeToPendingHint`

**Dependencies:** `./debug.js`, `./signal.js`

**Main flow:** Entry: `getPendingHintSnapshot()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/claudeDesktop.ts` (152 lines)

**Exports:**
- `getClaudeDesktopConfigPath`
- `readClaudeDesktopMcpServers`

**Dependencies:** `../services/mcp/types.js`, `./errors.js`, `./json.js`, `./log.js`, `./platform.js`

**Main flow:** Entry: `getClaudeDesktopConfigPath()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/claudemd.ts` (1479 lines)

**Exports:**
- `ExternalClaudeMdInclude`
- `MAX_MEMORY_CHARACTER_COUNT`
- `MemoryFileInfo`
- `clearMemoryFileCaches`
- `filterInjectedMemoryFiles`
- `getAllMemoryFilePaths`
- `getClaudeMds`
- `getConditionalRulesForCwdLevelDirectory`
- `getExternalClaudeMdIncludes`
- `getLargeMemoryFiles`
- `getManagedAndUserConditionalRules`
- `getMemoryFiles`
- `getMemoryFilesForNestedDirectory`
- `hasExternalClaudeMdIncludes`
- `isMemoryFilePath`
- `processConditionedMdRules`
- `processMdRules`
- `processMemoryFile`
- `resetGetMemoryFilesCache`
- `shouldShowClaudeMdExternalIncludesWarning`
- `stripHtmlComments`

**Dependencies:** `../bootstrap/state.js`, `../memdir/memdir.js`, `../memdir/paths.js`, `../services/analytics/growthbook.js`, `./config.js`, `./debug.js`, `./diagLogs.js`, `./envUtils.js`, `./errors.js`, `./file.js`

**Feature gates:** `TEAMMEM`

**Main flow:** Entry: `isMemoryFilePath()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/cleanupRegistry.ts` (25 lines)

**Exports:**
- `registerCleanup`
- `runCleanupFunctions`

**Dependencies:** local only

**Main flow:** Entry: `registerCleanup()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/cliArgs.ts` (60 lines)

**Exports:**
- `eagerParseCliFlag`
- `extractArgsAfterDoubleDash`

**Dependencies:** local only

**Main flow:** Entry: `eagerParseCliFlag()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/cliHighlight.ts` (54 lines)

**Exports:**
- `CliHighlight`
- `getCliHighlightPromise`
- `getLanguageName`

**Dependencies:** local only

**Main flow:** Entry: `getCliHighlightPromise()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/codeIndexing.ts` (206 lines)

**Exports:**
- `CodeIndexingTool`
- `detectCodeIndexingFromCommand`
- `detectCodeIndexingFromMcpServerName`
- `detectCodeIndexingFromMcpTool`

**Dependencies:** local only

**Main flow:** Entry: `CodeIndexingTool()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/collapseBackgroundBashNotifications.ts` (84 lines)

**Exports:**
- `collapseBackgroundBashNotifications`

**Dependencies:** `../constants/xml.js`, `../tasks/LocalShellTask/LocalShellTask.js`, `../types/message.js`, `./fullscreen.js`, `./messages.js`

**Main flow:** Entry: `collapseBackgroundBashNotifications()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/collapseHookSummaries.ts` (59 lines)

**Exports:**
- `collapseHookSummaries`

**Dependencies:** `../types/message.js`

**Main flow:** Entry: `collapseHookSummaries()`

**Behavior:** Hook lifecycle helper; registers callbacks or dispatches hook events.

## `utils/collapseReadSearch.ts` (1109 lines)

**Exports:**
- `SearchOrReadResult`
- `collapseReadSearchGroups`
- `getDisplayMessageFromCollapsed`
- `getSearchOrReadFromContent`
- `getSearchReadSummaryText`
- `getToolSearchOrReadInfo`
- `getToolUseIdsFromCollapsedGroup`
- `hasAnyToolInProgress`
- `summarizeRecentActivities`

**Dependencies:** `../Tool.js`, `../tools/BashTool/commentLabel.js`, `../tools/BashTool/toolName.js`, `../tools/FileEditTool/constants.js`, `../tools/FileWriteTool/prompt.js`, `../tools/REPLTool/constants.js`, `../tools/REPLTool/primitiveTools.js`, `../tools/ToolSearchTool/prompt.js`, `../tools/shared/gitOperationTracking.js`, `../types/message.js`

**Feature gates:** `HISTORY_SNIP`, `TEAMMEM`

**Main flow:** Entry: `getDisplayMessageFromCollapsed()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/collapseTeammateShutdowns.ts` (55 lines)

**Exports:**
- `collapseTeammateShutdowns`

**Dependencies:** `../types/message.js`

**Main flow:** Entry: `collapseTeammateShutdowns()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/combinedAbortSignal.ts` (47 lines)

**Exports:**
- `createCombinedAbortSignal`

**Dependencies:** `./abortController.js`

**Main flow:** Entry: `createCombinedAbortSignal()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/commandLifecycle.ts` (21 lines)

**Exports:**
- `notifyCommandLifecycle`
- `setCommandLifecycleListener`

**Dependencies:** local only

**Main flow:** Entry: `notifyCommandLifecycle()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/commitAttribution.ts` (961 lines)

**Exports:**
- `AttributionData`
- `AttributionState`
- `AttributionSummary`
- `FileAttribution`
- `attributionRestoreStateFromLog`
- `buildSurfaceKey`
- `calculateCommitAttribution`
- `computeContentHash`
- `createEmptyAttributionState`
- `expandFilePath`
- `getAttributionRepoRoot`
- `getClientSurface`
- `getFileMtime`
- `getGitDiffSize`
- `getRepoClassCached`
- `getStagedFiles`
- `incrementPromptCount`
- `isFileDeleted`
- `isGitTransientState`
- `isInternalModelRepo`
- `isInternalModelRepoCached`
- `normalizeFilePath`
- `restoreAttributionStateFromSnapshots`
- `sanitizeModelName`
- `sanitizeSurfaceKey`
- ... +5 more

**Dependencies:** `../bootstrap/state.js`, `../types/logs.js`, `./cwd.js`, `./debug.js`, `./execFileNoThrow.js`, `./fsOperations.js`, `./generatedFiles.js`, `./git.js`, `./git/gitFilesystem.js`, `./log.js`

**Main flow:** Entry: `isFileDeleted()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/completionCache.ts` (166 lines)

**Exports:**
- `regenerateCompletionCache`
- `setupShellCompletion`

**Dependencies:** `../components/design-system/color.js`, `../ink/supports-hyperlinks.js`, `./debug.js`, `./errors.js`, `./execFileNoThrow.js`, `./log.js`, `./theme.js`

**Main flow:** Entry: `setupShellCompletion()`

**Behavior:** In-memory or disk-backed cache with TTL/invalidation semantics.

## `utils/concurrentSessions.ts` (204 lines)

**Exports:**
- `SessionKind`
- `SessionStatus`
- `countConcurrentSessions`
- `isBgSession`
- `registerSession`
- `updateSessionActivity`
- `updateSessionBridgeId`
- `updateSessionName`

**Dependencies:** `../bootstrap/state.js`, `./cleanupRegistry.js`, `./debug.js`, `./envUtils.js`, `./errors.js`, `./genericProcessUtils.js`, `./platform.js`, `./slowOperations.js`, `./teammate.js`

**Feature gates:** `BG_SESSIONS`, `UDS_INBOX`

**Main flow:** Entry: `isBgSession()`

**Behavior:** Local session registry for multi-process dedup (bridge list, peer discovery).

## `utils/configConstants.ts` (21 lines)

**Exports:**
- `EDITOR_MODES`
- `NOTIFICATION_CHANNELS`
- `TEAMMATE_MODES`

**Dependencies:** local only

**Main flow:** Entry: `EDITOR_MODES()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/contentArray.ts` (51 lines)

**Exports:**
- `insertBlockAfterToolResults`

**Dependencies:** local only

**Main flow:** Entry: `insertBlockAfterToolResults()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/context.ts` (221 lines)

**Exports:**
- `CAPPED_DEFAULT_MAX_TOKENS`
- `COMPACT_MAX_OUTPUT_TOKENS`
- `ESCALATED_MAX_TOKENS`
- `MODEL_CONTEXT_WINDOW_DEFAULT`
- `calculateContextPercentages`
- `getContextWindowForModel`
- `getMaxThinkingTokensForModel`
- `getModelMaxOutputTokens`
- `getSonnet1mExpTreatmentEnabled`
- `has1mContext`
- `is1mContextDisabled`
- `modelSupports1M`

**Dependencies:** `../constants/betas.js`, `./config.js`, `./envUtils.js`, `./model/model.js`, `./model/modelCapabilities.js`

**Main flow:** Entry: `is1mContextDisabled()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/contextAnalysis.ts` (272 lines)

**Exports:**
- `analyzeContext`
- `tokenStatsToStatsigMetrics`

**Dependencies:** `../services/tokenEstimation.js`, `../types/message.js`, `./messages.js`, `./slowOperations.js`

**Main flow:** Entry: `analyzeContext()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/contextSuggestions.ts` (235 lines)

**Exports:**
- `ContextSuggestion`
- `SuggestionSeverity`
- `generateContextSuggestions`

**Dependencies:** `../tools/BashTool/toolName.js`, `../tools/FileReadTool/prompt.js`, `../tools/GrepTool/prompt.js`, `../tools/WebFetchTool/prompt.js`, `./analyzeContext.js`, `./file.js`, `./format.js`

**Main flow:** Entry: `ContextSuggestion()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/controlMessageCompat.ts` (32 lines)

**Exports:**
- `normalizeControlMessageKeys`

**Dependencies:** local only

**Main flow:** Entry: `normalizeControlMessageKeys()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/conversationRecovery.ts` (597 lines)

**Exports:**
- `DeserializeResult`
- `TeleportRemoteResponse`
- `TurnInterruptionState`
- `deserializeMessages`
- `deserializeMessagesWithInterruptDetection`
- `loadConversationForResume`
- `loadMessagesFromJsonlPath`
- `restoreSkillStateFromMessages`

**Dependencies:** `../bootstrap/state.js`, `../types/ids.js`, `../types/logs.js`, `../types/message.js`, `../types/permissions.js`, `./attachments.js`, `./fileHistory.js`, `./log.js`, `./messages.js`, `./plans.js`

**Feature gates:** `BG_SESSIONS`, `KAIROS`, `KAIROS_BRIEF`

**Main flow:** Entry: `loadConversationForResume()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/cron.ts` (308 lines)

**Exports:**
- `CronFields`
- `computeNextCronRun`
- `cronToHuman`
- `parseCronExpression`

**Dependencies:** local only

**Main flow:** Entry: `parseCronExpression()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/cronJitterConfig.ts` (75 lines)

**Exports:**
- `getCronJitterConfig`

**Dependencies:** `../services/analytics/growthbook.js`, `./cronTasks.js`, `./lazySchema.js`

**Main flow:** Entry: `getCronJitterConfig()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/cronScheduler.ts` (565 lines)

**Exports:**
- `CronScheduler`
- `buildMissedTaskNotification`
- `createCronScheduler`
- `isRecurringTaskAged`

**Dependencies:** `../bootstrap/state.js`, `../services/analytics/index.js`, `./cron.js`, `./cronTasks.js`, `./cronTasksLock.js`, `./debug.js`

**Main flow:** Entry: `isRecurringTaskAged()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/cronTasks.ts` (458 lines)

**Exports:**
- `CronJitterConfig`
- `CronTask`
- `DEFAULT_CRON_JITTER_CONFIG`
- `addCronTask`
- `findMissedTasks`
- `getCronFilePath`
- `hasCronTasksSync`
- `jitteredNextCronRunMs`
- `listAllCronTasks`
- `markCronTasksFired`
- `nextCronRunMs`
- `oneShotJitteredNextCronRunMs`
- `readCronTasks`
- `removeCronTasks`
- `writeCronTasks`

**Dependencies:** `../bootstrap/state.js`, `./cron.js`, `./debug.js`, `./errors.js`, `./fsOperations.js`, `./json.js`, `./log.js`, `./slowOperations.js`

**Main flow:** Entry: `getCronFilePath()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/cronTasksLock.ts` (195 lines)

**Exports:**
- `SchedulerLockOptions`
- `releaseSchedulerLock`
- `tryAcquireSchedulerLock`

**Dependencies:** `../bootstrap/state.js`, `./cleanupRegistry.js`, `./debug.js`, `./errors.js`, `./genericProcessUtils.js`, `./json.js`, `./lazySchema.js`, `./slowOperations.js`

**Main flow:** Entry: `SchedulerLockOptions()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/crossProjectResume.ts` (75 lines)

**Exports:**
- `CrossProjectResumeResult`
- `checkCrossProjectResume`

**Dependencies:** `../bootstrap/state.js`, `../types/logs.js`, `./bash/shellQuote.js`, `./sessionStorage.js`

**Main flow:** Entry: `CrossProjectResumeResult()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/Cursor.ts` (1530 lines)

**Exports:**
- `Cursor`
- `MeasuredText`
- `VIM_WORD_CHAR_REGEX`
- `WHITESPACE_REGEX`
- `canYankPop`
- `clearKillRing`
- `getKillRingItem`
- `getKillRingSize`
- `getLastKill`
- `isVimPunctuation`
- `isVimWhitespace`
- `isVimWordChar`
- `pushToKillRing`
- `recordYank`
- `resetKillAccumulation`
- `resetYankState`
- `updateYankLength`
- `yankPop`

**Dependencies:** `../ink/stringWidth.js`, `../ink/wrapAnsi.js`, `./intl.js`

**Main flow:** Entry: `isVimPunctuation()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/cwd.ts` (32 lines)

**Exports:**
- `getCwd`
- `pwd`
- `runWithCwdOverride`

**Dependencies:** `../bootstrap/state.js`

**Main flow:** Entry: `getCwd()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/debugFilter.ts` (157 lines)

**Exports:**
- `DebugFilter`
- `extractDebugCategories`
- `parseDebugFilter`
- `shouldShowDebugCategories`
- `shouldShowDebugMessage`

**Dependencies:** local only

**Main flow:** Entry: `parseDebugFilter()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/desktopDeepLink.ts` (236 lines)

**Exports:**
- `DesktopInstallStatus`
- `getDesktopInstallStatus`
- `openCurrentSessionInDesktop`

**Dependencies:** `../bootstrap/state.js`, `./cwd.js`, `./debug.js`, `./execFileNoThrow.js`, `./file.js`, `./semver.js`

**Main flow:** Entry: `getDesktopInstallStatus()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/detectRepository.ts` (178 lines)

**Exports:**
- `ParsedRepository`
- `clearRepositoryCaches`
- `detectCurrentRepository`
- `detectCurrentRepositoryWithHost`
- `getCachedRepository`
- `parseGitHubRepository`
- `parseGitRemote`

**Dependencies:** `./cwd.js`, `./debug.js`, `./git.js`

**Main flow:** Entry: `getCachedRepository()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/diagLogs.ts` (94 lines)

**Exports:**
- `logForDiagnosticsNoPII`
- `withDiagnosticsTiming`

**Dependencies:** `./fsOperations.js`, `./slowOperations.js`

**Main flow:** Entry: `logForDiagnosticsNoPII()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/diff.ts` (177 lines)

**Exports:**
- `CONTEXT_LINES`
- `DIFF_TIMEOUT_MS`
- `adjustHunkLineNumbers`
- `countLinesChanged`
- `getPatchForDisplay`
- `getPatchFromContents`

**Dependencies:** `../bootstrap/state.js`, `../cost-tracker.js`, `../tools/FileEditTool/types.js`, `./array.js`, `./file.js`

**Main flow:** Entry: `getPatchForDisplay()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/directMemberMessage.ts` (69 lines)

**Exports:**
- `DirectMessageResult`
- `parseDirectMemberMessage`
- `sendDirectMemberMessage`

**Dependencies:** `../state/AppState.js`

**Main flow:** Entry: `parseDirectMemberMessage()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/displayTags.ts` (51 lines)

**Exports:**
- `stripDisplayTags`
- `stripDisplayTagsAllowEmpty`
- `stripIdeContextTags`

**Dependencies:** local only

**Main flow:** Entry: `stripDisplayTags()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/doctorContextWarnings.ts` (265 lines)

**Exports:**
- `ContextWarning`
- `ContextWarnings`
- `checkContextWarnings`

**Dependencies:** `../Tool.js`, `../services/tokenEstimation.js`, `../tools/AgentTool/loadAgentsDir.js`, `./analyzeContext.js`, `./claudemd.js`, `./model/model.js`, `./permissions/permissionRuleParser.js`, `./permissions/shadowedRuleDetection.js`, `./sandbox/sandbox-adapter.js`, `./statusNoticeHelpers.js`

**Main flow:** Entry: `ContextWarning()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/doctorDiagnostic.ts` (625 lines)

**Exports:**
- `DiagnosticInfo`
- `InstallationType`
- `detectLinuxGlobPatternWarnings`
- `getCurrentInstallationType`
- `getDoctorDiagnostic`
- `getInvokedBinary`

**Dependencies:** `./autoUpdater.js`, `./bundledMode.js`, `./config.js`, `./cwd.js`, `./envUtils.js`, `./execFileNoThrow.js`, `./fsOperations.js`, `./localInstaller.js`, `./nativeInstaller/packageManagers.js`, `./platform.js`

**Main flow:** Entry: `getCurrentInstallationType()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/earlyInput.ts` (191 lines)

**Exports:**
- `consumeEarlyInput`
- `hasEarlyInput`
- `isCapturingEarlyInput`
- `seedEarlyInput`
- `startCapturingEarlyInput`
- `stopCapturingEarlyInput`

**Dependencies:** `./intl.js`

**Main flow:** Entry: `isCapturingEarlyInput()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/editor.ts` (183 lines)

**Exports:**
- `classifyGuiEditor`
- `getExternalEditor`
- `openFileInExternalEditor`

**Dependencies:** `../ink/instances.js`, `./debug.js`, `./which.js`

**Main flow:** Entry: `getExternalEditor()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/effort.ts` (329 lines)

**Exports:**
- `EFFORT_LEVELS`
- `EffortLevel`
- `EffortValue`
- `OpusDefaultEffortConfig`
- `convertEffortValueToLevel`
- `getDefaultEffortForModel`
- `getDisplayedEffortLevel`
- `getEffortEnvOverride`
- `getEffortLevelDescription`
- `getEffortSuffix`
- `getEffortValueDescription`
- `getInitialEffortSetting`
- `getOpusDefaultEffortConfig`
- `isEffortLevel`
- `isValidNumericEffort`
- `modelSupportsEffort`
- `modelSupportsMaxEffort`
- `parseEffortValue`
- `resolveAppliedEffort`
- `resolvePickerEffortPersistence`
- `toPersistableEffort`

**Dependencies:** `./auth.js`, `./envUtils.js`, `./model/modelSupportOverrides.js`, `./model/providers.js`, `./settings/settings.js`, `./thinking.js`

**Main flow:** Entry: `isEffortLevel()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/embeddedTools.ts` (29 lines)

**Exports:**
- `embeddedSearchToolsBinaryPath`
- `hasEmbeddedSearchTools`

**Dependencies:** `./envUtils.js`

**Main flow:** Entry: `embeddedSearchToolsBinaryPath()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/envDynamic.ts` (151 lines)

**Exports:**
- `envDynamic`
- `getTerminalWithJetBrainsDetection`
- `getTerminalWithJetBrainsDetectionAsync`
- `initJetBrainsDetection`

**Dependencies:** `./env.js`, `./envUtils.js`, `./execFileNoThrow.js`, `./genericProcessUtils.js`

**Feature gates:** `IS_LIBC_GLIBC`, `IS_LIBC_MUSL`

**Main flow:** Entry: `getTerminalWithJetBrainsDetection()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/envValidation.ts` (38 lines)

**Exports:**
- `EnvVarValidationResult`
- `validateBoundedIntEnvVar`

**Dependencies:** `./debug.js`

**Main flow:** Entry: `EnvVarValidationResult()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/errorLogSink.ts` (235 lines)

**Exports:**
- `_clearLogWritersForTesting`
- `_flushLogWritersForTesting`
- `getErrorsPath`
- `getMCPLogsPath`
- `initializeErrorLogSink`

**Dependencies:** `../bootstrap/state.js`, `./bufferedWriter.js`, `./cachePaths.js`, `./cleanupRegistry.js`, `./debug.js`, `./fsOperations.js`, `./log.js`, `./slowOperations.js`

**Main flow:** Entry: `getErrorsPath()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/exampleCommands.ts` (184 lines)

**Exports:**
- `countAndSortItems`
- `getExampleCommandFromCache`
- `pickDiverseCoreFiles`
- `refreshExampleCommands`

**Dependencies:** `../utils/cwd.js`, `./config.js`, `./env.js`, `./execFileNoThrow.js`, `./git.js`, `./log.js`, `./user.js`

**Main flow:** Entry: `getExampleCommandFromCache()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/execFileNoThrow.ts` (150 lines)

**Exports:**
- `execFileNoThrow`
- `execFileNoThrowWithCwd`

**Dependencies:** `../utils/cwd.js`, `./log.js`

**Main flow:** Entry: `execFileNoThrow()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/execFileNoThrowPortable.ts` (89 lines)

**Exports:**
- `execSyncWithDefaults_DEPRECATED`

**Dependencies:** `../utils/cwd.js`, `./slowOperations.js`

**Main flow:** Entry: `execSyncWithDefaults_DEPRECATED()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/execSyncWrapper.ts` (38 lines)

**Exports:**
- `execSync_DEPRECATED`

**Dependencies:** `./slowOperations.js`

**Main flow:** Entry: `execSync_DEPRECATED()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/extraUsage.ts` (23 lines)

**Exports:**
- `isBilledAsExtraUsage`

**Dependencies:** `./auth.js`, `./context.js`

**Main flow:** Entry: `isBilledAsExtraUsage()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/fastMode.ts` (532 lines)

**Exports:**
- `CooldownReason`
- `FAST_MODE_MODEL_DISPLAY`
- `FastModeDisabledReason`
- `FastModeRuntimeState`
- `clearFastModeCooldown`
- `getFastModeModel`
- `getFastModeRuntimeState`
- `getFastModeState`
- `getFastModeUnavailableReason`
- `getInitialFastModeSetting`
- `handleFastModeOverageRejection`
- `handleFastModeRejectedByAPI`
- `isFastModeAvailable`
- `isFastModeCooldown`
- `isFastModeEnabled`
- `isFastModeSupportedByModel`
- `onCooldownExpired`
- `onCooldownTriggered`
- `onFastModeOverageRejection`
- `onOrgFastModeChanged`
- `prefetchFastModeStatus`
- `resolveFastModeStatusFromCache`
- `triggerFastModeCooldown`

**Dependencies:** `../bootstrap/state.js`, `../services/analytics/index.js`, `./auth.js`, `./bundledMode.js`, `./config.js`, `./debug.js`, `./envUtils.js`, `./model/model.js`, `./model/providers.js`, `./privacyLevel.js`

**Main flow:** Entry: `isFastModeAvailable()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/fileHistory.ts` (1115 lines)

**Exports:**
- `DiffStats`
- `FileHistoryBackup`
- `FileHistorySnapshot`
- `FileHistoryState`
- `checkOriginFileChanged`
- `copyFileHistoryForResume`
- `fileHistoryCanRestore`
- `fileHistoryEnabled`
- `fileHistoryGetDiffStats`
- `fileHistoryHasAnyChanges`
- `fileHistoryMakeSnapshot`
- `fileHistoryRestoreStateFromLog`
- `fileHistoryRewind`
- `fileHistoryTrackEdit`

**Dependencies:** `./config.js`, `./debug.js`, `./envUtils.js`, `./errors.js`, `./file.js`, `./log.js`, `./sessionStorage.js`

**Main flow:** Entry: `DiffStats()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/fileOperationAnalytics.ts` (71 lines)

**Exports:**
- `logFileOperation`

**Dependencies:** local only

**Main flow:** Entry: `logFileOperation()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/fileRead.ts` (102 lines)

**Exports:**
- `LineEndingType`
- `detectEncodingForResolvedPath`
- `detectLineEndingsForString`
- `readFileSync`
- `readFileSyncWithMetadata`

**Dependencies:** `./debug.js`, `./fsOperations.js`

**Main flow:** Entry: `LineEndingType()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/fileReadCache.ts` (96 lines)

**Exports:**
- `fileReadCache`

**Dependencies:** `./file.js`, `./fsOperations.js`

**Main flow:** Entry: `fileReadCache()`

**Behavior:** In-memory or disk-backed cache with TTL/invalidation semantics.

## `utils/fileStateCache.ts` (142 lines)

**Exports:**
- `FileState`
- `FileStateCache`
- `READ_FILE_STATE_CACHE_SIZE`
- `cacheKeys`
- `cacheToObject`
- `cloneFileStateCache`
- `createFileStateCacheWithSizeLimit`
- `mergeFileStateCaches`

**Dependencies:** local only

**Main flow:** Entry: `createFileStateCacheWithSizeLimit()`

**Behavior:** In-memory or disk-backed cache with TTL/invalidation semantics.

## `utils/findExecutable.ts` (17 lines)

**Exports:**
- `findExecutable`

**Dependencies:** `./which.js`

**Main flow:** Entry: `findExecutable()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/fingerprint.ts` (76 lines)

**Exports:**
- `FINGERPRINT_SALT`
- `computeFingerprint`
- `computeFingerprintFromMessages`
- `extractFirstMessageText`

**Dependencies:** `../types/message.js`

**Main flow:** Entry: `FINGERPRINT_SALT()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/forkedAgent.ts` (689 lines)

**Exports:**
- `CacheSafeParams`
- `ForkedAgentParams`
- `ForkedAgentResult`
- `PreparedForkedContext`
- `SubagentContextOverrides`
- `createCacheSafeParams`
- `createGetAppStateWithAllowedTools`
- `createSubagentContext`
- `extractResultText`
- `getLastCacheSafeParams`
- `prepareForkedCommandContext`
- `runForkedAgent`
- `saveCacheSafeParams`

**Dependencies:** `../Tool.js`, `../commands.js`, `../constants/querySource.js`, `../hooks/useCanUseTool.js`, `../query.js`, `../services/analytics/index.js`, `../services/api/claude.js`, `../services/api/logging.js`, `../tools/AgentTool/loadAgentsDir.js`, `../types/ids.js`

**Main flow:** Entry: `getLastCacheSafeParams()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/formatBriefTimestamp.ts` (81 lines)

**Exports:**
- `formatBriefTimestamp`

**Dependencies:** local only

**Main flow:** Entry: `formatBriefTimestamp()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/fpsTracker.ts` (47 lines)

**Exports:**
- `FpsMetrics`
- `FpsTracker`

**Dependencies:** local only

**Main flow:** Entry: `FpsMetrics()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/frontmatterParser.ts` (370 lines)

**Exports:**
- `FRONTMATTER_REGEX`
- `FrontmatterData`
- `FrontmatterShell`
- `ParsedMarkdown`
- `coerceDescriptionToString`
- `parseBooleanFrontmatter`
- `parseFrontmatter`
- `parsePositiveIntFromFrontmatter`
- `parseShellFrontmatter`
- `splitPathInFrontmatter`

**Dependencies:** `./debug.js`, `./settings/types.js`, `./yaml.js`

**Main flow:** Entry: `parseBooleanFrontmatter()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/fsOperations.ts` (770 lines)

**Exports:**
- `FsOperations`
- `NodeFsOperations`
- `ReadFileRangeResult`
- `getFsImplementation`
- `getPathsForPermissionCheck`
- `isDuplicatePath`
- `readFileRange`
- `resolveDeepestExistingAncestorSync`
- `safeResolvePath`
- `setFsImplementation`
- `setOriginalFsImplementation`
- `tailFile`

**Dependencies:** `./errors.js`, `./slowOperations.js`

**Main flow:** Entry: `isDuplicatePath()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/fullscreen.ts` (202 lines)

**Exports:**
- `_resetForTesting`
- `_resetTmuxControlModeProbeForTesting`
- `isFullscreenActive`
- `isFullscreenEnvEnabled`
- `isMouseClicksDisabled`
- `isMouseTrackingEnabled`
- `isTmuxControlMode`
- `maybeGetTmuxMouseHint`

**Dependencies:** `../bootstrap/state.js`, `./debug.js`, `./envUtils.js`, `./execFileNoThrow.js`

**Main flow:** Entry: `isFullscreenActive()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/generatedFiles.ts` (136 lines)

**Exports:**
- `filterGeneratedFiles`
- `isGeneratedFile`

**Dependencies:** local only

**Main flow:** Entry: `isGeneratedFile()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/generators.ts` (88 lines)

**Exports:**
- `lastX`
- `returnValue`
- `toArray`

**Dependencies:** local only

**Main flow:** Entry: `lastX()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/genericProcessUtils.ts` (184 lines)

**Exports:**
- `getAncestorCommandsAsync`
- `getAncestorPidsAsync`
- `getChildPids`
- `getProcessCommand`
- `isProcessRunning`

**Dependencies:** `./execFileNoThrow.js`

**Main flow:** Entry: `isProcessRunning()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/getWorktreePaths.ts` (70 lines)

**Exports:**
- `getWorktreePaths`

**Dependencies:** `../services/analytics/index.js`, `./execFileNoThrow.js`, `./git.js`

**Main flow:** Entry: `getWorktreePaths()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/getWorktreePathsPortable.ts` (27 lines)

**Exports:**
- `getWorktreePathsPortable`

**Dependencies:** local only

**Main flow:** Entry: `getWorktreePathsPortable()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/ghPrStatus.ts` (106 lines)

**Exports:**
- `PrReviewState`
- `PrStatus`
- `deriveReviewState`
- `fetchPrStatus`

**Dependencies:** `./execFileNoThrow.js`, `./git.js`, `./slowOperations.js`

**Main flow:** Entry: `PrReviewState()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/gitDiff.ts` (532 lines)

**Exports:**
- `GitDiffResult`
- `GitDiffStats`
- `NumstatResult`
- `PerFileStats`
- `ToolUseDiff`
- `fetchGitDiff`
- `fetchGitDiffHunks`
- `fetchSingleFileGitDiff`
- `parseGitDiff`
- `parseGitNumstat`
- `parseShortstat`

**Dependencies:** `./cwd.js`, `./detectRepository.js`, `./execFileNoThrow.js`, `./file.js`, `./git.js`

**Main flow:** Entry: `parseGitDiff()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/githubRepoPathMapping.ts` (162 lines)

**Exports:**
- `filterExistingPaths`
- `getKnownPathsForRepo`
- `removePathFromRepo`
- `updateGithubRepoPathMapping`
- `validateRepoAtPath`

**Dependencies:** `../bootstrap/state.js`, `./config.js`, `./debug.js`, `./detectRepository.js`, `./file.js`, `./git.js`, `./git/gitFilesystem.js`

**Main flow:** Entry: `getKnownPathsForRepo()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/gitSettings.ts` (18 lines)

**Exports:**
- `shouldIncludeGitInstructions`

**Dependencies:** `./envUtils.js`, `./settings/settings.js`

**Main flow:** Entry: `shouldIncludeGitInstructions()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/glob.ts` (130 lines)

**Exports:**
- `extractGlobBaseDirectory`
- `glob`

**Dependencies:** `../Tool.js`, `./envUtils.js`, `./permissions/filesystem.js`, `./platform.js`, `./plugins/orphanedPluginFilter.js`, `./ripgrep.js`

**Main flow:** Entry: `extractGlobBaseDirectory()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/gracefulShutdown.ts` (529 lines)

**Exports:**
- `getPendingShutdownForTesting`
- `gracefulShutdown`
- `gracefulShutdownSync`
- `isShuttingDown`
- `resetShutdownState`
- `setupGracefulShutdown`

**Dependencies:** `../bootstrap/state.js`, `../ink/instances.js`, `../ink/termio/csi.js`, `../ink/termio/dec.js`, `../ink/termio/osc.js`, `../services/analytics/datadog.js`, `../services/analytics/firstPartyEventLogger.js`, `../services/analytics/index.js`, `../state/AppState.js`, `./cleanupRegistry.js`

**Main flow:** Entry: `isShuttingDown()`

**Behavior:** Coordinates shutdown deadline, hook flush, and background task teardown.

## `utils/groupToolUses.ts` (182 lines)

**Exports:**
- `GroupingResult`
- `MessageWithoutProgress`
- `applyGrouping`

**Dependencies:** `../Tool.js`, `../types/message.js`

**Main flow:** Entry: `GroupingResult()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/handlePromptSubmit.ts` (610 lines)

**Exports:**
- `HandlePromptSubmitParams`
- `PromptInputHelpers`
- `handlePromptSubmit`

**Dependencies:** `../Tool.js`, `../commands.js`, `../components/MessageSelector.js`, `../components/Spinner/types.js`, `../constants/querySource.js`, `../history.js`, `../hooks/useCanUseTool.js`, `../hooks/useIdeSelection.js`, `../state/AppState.js`, `../types/command.js`

**Main flow:** Entry: `handlePromptSubmit()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/hash.ts` (46 lines)

**Exports:**
- `djb2Hash`
- `hashContent`
- `hashPair`

**Dependencies:** local only

**Main flow:** Entry: `djb2Hash()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/headlessProfiler.ts` (178 lines)

**Exports:**
- `headlessProfilerCheckpoint`
- `headlessProfilerStartTurn`
- `logHeadlessProfilerTurn`

**Dependencies:** `../bootstrap/state.js`, `../services/analytics/index.js`, `./debug.js`, `./envUtils.js`, `./profilerBase.js`, `./slowOperations.js`

**Main flow:** Entry: `headlessProfilerCheckpoint()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/heapDumpService.ts` (303 lines)

**Exports:**
- `HeapDumpResult`
- `MemoryDiagnostics`
- `captureMemoryDiagnostics`
- `performHeapDump`

**Dependencies:** `../bootstrap/state.js`, `../services/analytics/index.js`, `./debug.js`, `./errors.js`, `./file.js`, `./fsOperations.js`, `./log.js`, `./slowOperations.js`

**Main flow:** Entry: `HeapDumpResult()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/heatmap.ts` (198 lines)

**Exports:**
- `HeatmapOptions`
- `generateHeatmap`

**Dependencies:** `./stats.js`, `./statsCache.js`

**Main flow:** Entry: `HeatmapOptions()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/horizontalScroll.ts` (137 lines)

**Exports:**
- `HorizontalScrollWindow`
- `calculateHorizontalScrollWindow`

**Dependencies:** local only

**Main flow:** Entry: `HorizontalScrollWindow()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/http.ts` (136 lines)

**Exports:**
- `AuthHeaders`
- `getAuthHeaders`
- `getMCPUserAgent`
- `getUserAgent`
- `getWebFetchUserAgent`
- `withOAuth401Retry`

**Dependencies:** `../constants/oauth.js`, `./auth.js`, `./userAgent.js`, `./workloadContext.js`

**Main flow:** Entry: `getAuthHeaders()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/hyperlink.ts` (39 lines)

**Exports:**
- `OSC8_END`
- `OSC8_START`
- `createHyperlink`

**Dependencies:** `../ink/supports-hyperlinks.js`

**Main flow:** Entry: `createHyperlink()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/ide.ts` (1494 lines)

**Exports:**
- `DetectedIDEInfo`
- `IDEExtensionInstallationStatus`
- `IdeType`
- `cleanupStaleIdeLockfiles`
- `closeOpenDiffs`
- `detectIDEs`
- `detectRunningIDEs`
- `detectRunningIDEsCached`
- `findAvailableIDE`
- `getConnectedIdeClient`
- `getConnectedIdeName`
- `getIdeClientName`
- `getIdeLockfilesPaths`
- `getSortedIdeLockfiles`
- `getTerminalIdeType`
- `hasAccessToIDEExtensionDiffFeature`
- `initializeIdeIntegration`
- `isCursorInstalled`
- `isIDEExtensionInstalled`
- `isJetBrainsIde`
- `isSupportedJetBrainsTerminal`
- `isSupportedTerminal`
- `isSupportedVSCodeTerminal`
- `isVSCodeIde`
- `isVSCodeInstalled`
- ... +5 more

**Dependencies:** `../bootstrap/state.js`, `../services/mcp/client.js`, `../services/mcp/types.js`, `./abortController.js`, `./config.js`, `./debug.js`, `./env.js`, `./envDynamic.js`, `./envUtils.js`, `./errors.js`

**Main flow:** Entry: `isCursorInstalled()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/idePathConversion.ts` (90 lines)

**Exports:**
- `IDEPathConverter`
- `WindowsToWSLConverter`
- `checkWSLDistroMatch`

**Dependencies:** local only

**Main flow:** Entry: `IDEPathConverter()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/idleTimeout.ts` (53 lines)

**Exports:**
- `createIdleTimeoutManager`

**Dependencies:** `./debug.js`, `./gracefulShutdown.js`

**Main flow:** Entry: `createIdleTimeoutManager()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/imagePaste.ts` (416 lines)

**Exports:**
- `IMAGE_EXTENSION_REGEX`
- `ImageWithDimensions`
- `PASTE_THRESHOLD`
- `asImageFilePath`
- `getImageFromClipboard`
- `getImagePathFromClipboard`
- `hasImageInClipboard`
- `isImageFilePath`
- `tryReadImageFromPath`

**Dependencies:** `../constants/apiLimits.js`, `../services/analytics/growthbook.js`, `../tools/FileReadTool/imageProcessor.js`, `./debug.js`, `./execFileNoThrow.js`, `./fsOperations.js`, `./imageResizer.js`, `./log.js`

**Feature gates:** `NATIVE_CLIPBOARD_IMAGE`

**Main flow:** Entry: `isImageFilePath()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/imageResizer.ts` (880 lines)

**Exports:**
- `ImageBlockWithDimensions`
- `ImageDimensions`
- `ImageResizeError`
- `ResizeResult`
- `compressImageBlock`
- `compressImageBuffer`
- `compressImageBufferWithTokenLimit`
- `createImageMetadataText`
- `detectImageFormatFromBase64`
- `detectImageFormatFromBuffer`
- `maybeResizeAndDownsampleImageBlock`
- `maybeResizeAndDownsampleImageBuffer`

**Dependencies:** `../constants/apiLimits.js`, `../services/analytics/index.js`, `../tools/FileReadTool/imageProcessor.js`, `./debug.js`, `./errors.js`, `./format.js`, `./log.js`

**Main flow:** Entry: `createImageMetadataText()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/imageStore.ts` (167 lines)

**Exports:**
- `cacheImagePath`
- `cleanupOldImageCaches`
- `clearStoredImagePaths`
- `getStoredImagePath`
- `storeImage`
- `storeImages`

**Dependencies:** `../bootstrap/state.js`, `./config.js`, `./debug.js`, `./envUtils.js`, `./fsOperations.js`

**Main flow:** Entry: `getStoredImagePath()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/imageValidation.ts` (104 lines)

**Exports:**
- `ImageSizeError`
- `OversizedImage`
- `validateImagesForAPI`

**Dependencies:** `../constants/apiLimits.js`, `../services/analytics/index.js`, `./format.js`

**Main flow:** Entry: `ImageSizeError()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/immediateCommand.ts` (15 lines)

**Exports:**
- `shouldInferenceConfigCommandBeImmediate`

**Dependencies:** `../services/analytics/growthbook.js`

**Main flow:** Entry: `shouldInferenceConfigCommandBeImmediate()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/ink.ts` (26 lines)

**Exports:**
- `toInkColor`

**Dependencies:** `../ink.js`, `../tools/AgentTool/agentColorManager.js`

**Main flow:** Entry: `toInkColor()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/inProcessTeammateHelpers.ts` (102 lines)

**Exports:**
- `findInProcessTeammateTaskId`
- `handlePlanApprovalResponse`
- `isPermissionRelatedResponse`
- `setAwaitingPlanApproval`

**Dependencies:** `../state/AppState.js`, `../tasks/InProcessTeammateTask/types.js`, `./task/framework.js`, `./teammateMailbox.js`

**Main flow:** Entry: `isPermissionRelatedResponse()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/intl.ts` (94 lines)

**Exports:**
- `firstGrapheme`
- `getGraphemeSegmenter`
- `getRelativeTimeFormat`
- `getSystemLocaleLanguage`
- `getTimeZone`
- `getWordSegmenter`
- `lastGrapheme`

**Dependencies:** local only

**Main flow:** Entry: `getGraphemeSegmenter()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/iTermBackup.ts` (73 lines)

**Exports:**
- `checkAndRestoreITerm2Backup`
- `markITerm2SetupComplete`

**Dependencies:** `./config.js`, `./log.js`

**Main flow:** Entry: `checkAndRestoreITerm2Backup()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/jetbrains.ts` (191 lines)

**Exports:**
- `isJetBrainsPluginInstalled`
- `isJetBrainsPluginInstalledCached`
- `isJetBrainsPluginInstalledCachedSync`

**Dependencies:** `../utils/fsOperations.js`, `./ide.js`

**Main flow:** Entry: `isJetBrainsPluginInstalled()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/json.ts` (277 lines)

**Exports:**
- `addItemToJSONCArray`
- `parseJSONL`
- `readJSONLFile`
- `safeParseJSON`
- `safeParseJSONC`

**Dependencies:** `./jsonRead.js`, `./log.js`, `./memoize.js`, `./slowOperations.js`

**Main flow:** Entry: `parseJSONL()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/jsonRead.ts` (16 lines)

**Exports:**
- `stripBOM`

**Dependencies:** local only

**Main flow:** Entry: `stripBOM()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/keyboardShortcuts.ts` (14 lines)

**Exports:**
- `MACOS_OPTION_SPECIAL_CHARS`
- `isMacosOptionChar`

**Dependencies:** local only

**Main flow:** Entry: `isMacosOptionChar()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/lazySchema.ts` (8 lines)

**Exports:**
- `lazySchema`

**Dependencies:** local only

**Main flow:** Entry: `lazySchema()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/listSessionsImpl.ts` (454 lines)

**Exports:**
- `ListSessionsOptions`
- `SessionInfo`
- `listCandidates`
- `listSessionsImpl`
- `parseSessionInfoFromLite`

**Dependencies:** `./getWorktreePathsPortable.js`, `./sessionStoragePortable.js`

**Main flow:** Entry: `parseSessionInfoFromLite()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/localInstaller.ts` (162 lines)

**Exports:**
- `ensureLocalPackageEnvironment`
- `getLocalClaudePath`
- `getShellType`
- `installOrUpdateClaudePackage`
- `isRunningFromLocalInstallation`
- `localInstallationExists`

**Dependencies:** `./config.js`, `./envUtils.js`, `./errors.js`, `./execFileNoThrow.js`, `./fsOperations.js`, `./log.js`, `./slowOperations.js`

**Main flow:** Entry: `isRunningFromLocalInstallation()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/lockfile.ts` (43 lines)

**Exports:**
- `check`
- `lock`
- `lockSync`
- `unlock`

**Dependencies:** local only

**Main flow:** Entry: `check()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/logoV2Utils.ts` (350 lines)

**Exports:**
- `LayoutDimensions`
- `LayoutMode`
- `calculateLayoutDimensions`
- `calculateOptimalLeftWidth`
- `formatModelAndBilling`
- `formatReleaseNoteForDisplay`
- `formatWelcomeMessage`
- `getLayoutMode`
- `getLogoDisplayData`
- `getRecentActivity`
- `getRecentActivitySync`
- `getRecentReleaseNotesSync`
- `truncatePath`

**Dependencies:** `../bootstrap/state.js`, `../ink/stringWidth.js`, `../types/logs.js`, `./auth.js`, `./cwd.js`, `./file.js`, `./format.js`, `./releaseNotes.js`, `./semver.js`, `./sessionStorage.js`

**Main flow:** Entry: `getLayoutMode()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/mailbox.ts` (73 lines)

**Exports:**
- `Mailbox`
- `Message`
- `MessageSource`

**Dependencies:** `./signal.js`

**Main flow:** Entry: `Mailbox()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/managedEnv.ts` (199 lines)

**Exports:**
- `applyConfigEnvironmentVariables`
- `applySafeConfigEnvironmentVariables`

**Dependencies:** `../services/remoteManagedSettings/syncCache.js`, `./caCerts.js`, `./config.js`, `./envUtils.js`, `./managedEnvConstants.js`, `./mtls.js`, `./proxy.js`, `./settings/constants.js`, `./settings/settings.js`

**Main flow:** Entry: `applyConfigEnvironmentVariables()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/managedEnvConstants.ts` (191 lines)

**Exports:**
- `DANGEROUS_SHELL_SETTINGS`
- `SAFE_ENV_VARS`
- `isProviderManagedEnvVar`

**Dependencies:** local only

**Main flow:** Entry: `isProviderManagedEnvVar()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/markdown.ts` (381 lines)

**Exports:**
- `applyMarkdown`
- `configureMarked`
- `formatToken`
- `padAligned`

**Dependencies:** `../components/design-system/color.js`, `../constants/figures.js`, `../ink/stringWidth.js`, `../ink/supports-hyperlinks.js`, `./cliHighlight.js`, `./debug.js`, `./hyperlink.js`, `./messages.js`, `./theme.js`

**Main flow:** Entry: `applyMarkdown()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/markdownConfigLoader.ts` (600 lines)

**Exports:**
- `CLAUDE_CONFIG_DIRECTORIES`
- `ClaudeConfigDirectory`
- `MarkdownFile`
- `extractDescriptionFromMarkdown`
- `getProjectDirsUpToHome`
- `loadMarkdownFilesForSubdir`
- `parseAgentToolsFromFrontmatter`
- `parseSlashCommandToolsFromFrontmatter`

**Dependencies:** `../bootstrap/state.js`, `./debug.js`, `./envUtils.js`, `./errors.js`, `./file.js`, `./frontmatterParser.js`, `./git.js`, `./permissions/permissionSetup.js`, `./ripgrep.js`, `./settings/constants.js`

**Feature gates:** `TEMPLATES`

**Main flow:** Entry: `getProjectDirsUpToHome()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/mcpInstructionsDelta.ts` (130 lines)

**Exports:**
- `ClientSideInstruction`
- `McpInstructionsDelta`
- `getMcpInstructionsDelta`
- `isMcpInstructionsDeltaEnabled`

**Dependencies:** `../services/analytics/growthbook.js`, `../services/analytics/index.js`, `../services/mcp/types.js`, `../types/message.js`, `./envUtils.js`

**Main flow:** Entry: `isMcpInstructionsDeltaEnabled()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/mcpOutputStorage.ts` (189 lines)

**Exports:**
- `PersistBinaryResult`
- `extensionForMimeType`
- `getBinaryBlobSavedMessage`
- `getFormatDescription`
- `getLargeOutputInstructions`
- `isBinaryContentType`
- `persistBinaryContent`

**Dependencies:** `../services/analytics/index.js`, `../services/mcp/client.js`, `./errors.js`, `./format.js`, `./log.js`, `./toolResultStorage.js`

**Main flow:** Entry: `isBinaryContentType()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/mcpValidation.ts` (208 lines)

**Exports:**
- `IMAGE_TOKEN_ESTIMATE`
- `MCPToolResult`
- `MCP_TOKEN_COUNT_THRESHOLD_FACTOR`
- `getContentSizeEstimate`
- `getMaxMcpOutputTokens`
- `mcpContentNeedsTruncation`
- `truncateMcpContent`
- `truncateMcpContentIfNeeded`

**Dependencies:** `../services/analytics/growthbook.js`, `../services/tokenEstimation.js`, `./imageResizer.js`, `./log.js`

**Main flow:** Entry: `getContentSizeEstimate()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/mcpWebSocketTransport.ts` (200 lines)

**Exports:**
- `WebSocketTransport`

**Dependencies:** `./diagLogs.js`, `./errors.js`, `./slowOperations.js`

**Main flow:** Entry: `WebSocketTransport()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/memoize.ts` (269 lines)

**Exports:**
- `memoizeWithLRU`
- `memoizeWithTTL`
- `memoizeWithTTLAsync`

**Dependencies:** `./log.js`, `./slowOperations.js`

**Main flow:** Entry: `memoizeWithLRU()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/memoryFileDetection.ts` (289 lines)

**Exports:**
- `MemoryScope`
- `detectSessionFileType`
- `detectSessionPatternType`
- `isAutoManagedMemoryFile`
- `isAutoManagedMemoryPattern`
- `isAutoMemFile`
- `isMemoryDirectory`
- `isShellCommandTargetingMemory`
- `memoryScopeForPath`

**Dependencies:** `../memdir/paths.js`, `../tools/AgentTool/agentMemory.js`, `./envUtils.js`, `./windowsPaths.js`

**Feature gates:** `TEAMMEM`

**Main flow:** Entry: `isAutoManagedMemoryFile()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/messagePredicates.ts` (8 lines)

**Exports:**
- `isHumanTurn`

**Dependencies:** `../types/message.js`

**Main flow:** Entry: `isHumanTurn()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/messageQueueManager.ts` (547 lines)

**Exports:**
- `PopAllEditableResult`
- `SetAppState`
- `clearCommandQueue`
- `clearPendingNotifications`
- `dequeue`
- `dequeueAll`
- `dequeueAllMatching`
- `dequeuePendingNotification`
- `enqueue`
- `enqueuePendingNotification`
- `getCommandQueue`
- `getCommandQueueLength`
- `getCommandQueueSnapshot`
- `getCommandsByMaxPriority`
- `getPendingNotificationsCount`
- `getPendingNotificationsSnapshot`
- `hasCommandsInQueue`
- `hasPendingNotifications`
- `isPromptInputModeEditable`
- `isQueuedCommandEditable`
- `isQueuedCommandVisible`
- `isSlashCommand`
- `peek`
- `popAllEditable`
- `recheckCommandQueue`
- ... +7 more

**Dependencies:** `../bootstrap/state.js`, `../state/AppState.js`, `../types/messageQueueTypes.js`, `../types/textInputTypes.js`, `./config.js`, `./messages.js`, `./objectGroupBy.js`, `./sessionStorage.js`, `./signal.js`

**Feature gates:** `KAIROS`, `KAIROS_CHANNELS`

**Main flow:** Entry: `isPromptInputModeEditable()`

**Behavior:** FIFO command queue with peek/dequeue and slash-command visibility hooks.

## `utils/modelCost.ts` (231 lines)

**Exports:**
- `COST_HAIKU_35`
- `COST_HAIKU_45`
- `COST_TIER_15_75`
- `COST_TIER_30_150`
- `COST_TIER_3_15`
- `COST_TIER_5_25`
- `MODEL_COSTS`
- `ModelCosts`
- `calculateCostFromTokens`
- `calculateUSDCost`
- `formatModelPricing`
- `getModelCosts`
- `getModelPricingString`
- `getOpus46CostTier`

**Dependencies:** `../bootstrap/state.js`, `./fastMode.js`, `./model/configs.js`, `./model/model.js`

**Main flow:** Entry: `getModelCosts()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/modifiers.ts` (36 lines)

**Exports:**
- `ModifierKey`
- `isModifierPressed`
- `prewarmModifiers`

**Dependencies:** local only

**Main flow:** Entry: `isModifierPressed()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/mtls.ts` (179 lines)

**Exports:**
- `MTLSConfig`
- `TLSConfig`
- `clearMTLSCache`
- `configureGlobalMTLS`
- `getMTLSAgent`
- `getMTLSConfig`
- `getTLSFetchOptions`
- `getWebSocketTLSOptions`

**Dependencies:** `./caCerts.js`, `./debug.js`, `./fsOperations.js`

**Main flow:** Entry: `getMTLSAgent()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/notebook.ts` (224 lines)

**Exports:**
- `mapNotebookCellsToToolResult`
- `parseCellId`
- `readNotebook`

**Dependencies:** `../tools/BashTool/toolName.js`, `../tools/BashTool/utils.js`, `../types/notebook.js`, `./fsOperations.js`, `./path.js`, `./slowOperations.js`

**Main flow:** Entry: `parseCellId()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/pasteStore.ts` (104 lines)

**Exports:**
- `cleanupOldPastes`
- `hashPastedText`
- `retrievePastedText`
- `storePastedText`

**Dependencies:** `./debug.js`, `./envUtils.js`, `./errors.js`

**Main flow:** Entry: `cleanupOldPastes()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/pdf.ts` (300 lines)

**Exports:**
- `PDFError`
- `PDFExtractPagesResult`
- `PDFResult`
- `extractPDFPages`
- `getPDFPageCount`
- `isPdftoppmAvailable`
- `readPDF`
- `resetPdftoppmCache`

**Dependencies:** `../constants/apiLimits.js`, `./errors.js`, `./execFileNoThrow.js`, `./format.js`, `./fsOperations.js`, `./toolResultStorage.js`

**Main flow:** Entry: `isPdftoppmAvailable()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/pdfUtils.ts` (70 lines)

**Exports:**
- `DOCUMENT_EXTENSIONS`
- `isPDFExtension`
- `isPDFSupported`
- `parsePDFPageRange`

**Dependencies:** `./model/model.js`

**Main flow:** Entry: `isPDFExtension()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/peerAddress.ts` (21 lines)

**Exports:**
- `parseAddress`

**Dependencies:** local only

**Main flow:** Entry: `parseAddress()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/planModeV2.ts` (95 lines)

**Exports:**
- `PewterLedgerVariant`
- `getPewterLedgerVariant`
- `getPlanModeV2AgentCount`
- `getPlanModeV2ExploreAgentCount`
- `isPlanModeInterviewPhaseEnabled`

**Dependencies:** `../services/analytics/growthbook.js`, `./auth.js`, `./envUtils.js`

**Main flow:** Entry: `isPlanModeInterviewPhaseEnabled()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/plans.ts` (397 lines)

**Exports:**
- `clearAllPlanSlugs`
- `clearPlanSlug`
- `copyPlanForFork`
- `copyPlanForResume`
- `getPlan`
- `getPlanFilePath`
- `getPlanSlug`
- `getPlansDirectory`
- `persistFileSnapshotIfRemote`
- `setPlanSlug`

**Dependencies:** `../bootstrap/state.js`, `../tools/ExitPlanModeTool/constants.js`, `./cwd.js`, `./debug.js`, `./envUtils.js`, `./errors.js`, `./filePersistence/outputsScanner.js`, `./fsOperations.js`, `./log.js`, `./settings/settings.js`

**Main flow:** Entry: `getPlan()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/privacyLevel.ts` (55 lines)

**Exports:**
- `getEssentialTrafficOnlyReason`
- `getPrivacyLevel`
- `isEssentialTrafficOnly`
- `isTelemetryDisabled`

**Dependencies:** local only

**Main flow:** Entry: `isEssentialTrafficOnly()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/profilerBase.ts` (46 lines)

**Exports:**
- `formatMs`
- `formatTimelineLine`
- `getPerformance`

**Dependencies:** `./format.js`

**Main flow:** Entry: `getPerformance()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/promptCategory.ts` (49 lines)

**Exports:**
- `getQuerySourceForAgent`
- `getQuerySourceForREPL`

**Dependencies:** `../constants/outputStyles.js`, `./settings/settings.js`

**Main flow:** Entry: `getQuerySourceForAgent()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/promptEditor.ts` (188 lines)

**Exports:**
- `EditorResult`
- `editFileInEditor`
- `editPromptInEditor`

**Dependencies:** `../history.js`, `../ink/instances.js`, `./config.js`, `./editor.js`, `./execSyncWrapper.js`, `./fsOperations.js`, `./ide.js`, `./slowOperations.js`, `./tempfile.js`

**Main flow:** Entry: `EditorResult()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/promptShellExecution.ts` (183 lines)

**Exports:**
- `executeShellCommandsInPrompt`

**Dependencies:** `../Tool.js`, `../tools/BashTool/BashTool.js`, `./debug.js`, `./errors.js`, `./frontmatterParser.js`, `./messages.js`, `./permissions/permissions.js`, `./shell/shellToolUtils.js`, `./toolResultStorage.js`

**Main flow:** Entry: `executeShellCommandsInPrompt()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/proxy.ts` (426 lines)

**Exports:**
- `_resetKeepAliveForTesting`
- `clearProxyCache`
- `configureGlobalAgents`
- `createAxiosInstance`
- `disableKeepAlive`
- `getAWSClientProxyConfig`
- `getAddressFamily`
- `getNoProxy`
- `getProxyAgent`
- `getProxyFetchOptions`
- `getProxyUrl`
- `getWebSocketProxyAgent`
- `getWebSocketProxyUrl`
- `shouldBypassProxy`

**Dependencies:** `./caCerts.js`, `./debug.js`, `./envUtils.js`, `./mtls.js`

**Main flow:** Entry: `getAWSClientProxyConfig()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/queryContext.ts` (179 lines)

**Exports:**
- `buildSideQuestionFallbackParams`
- `fetchSystemPromptParts`

**Dependencies:** `../Tool.js`, `../commands.js`, `../constants/prompts.js`, `../context.js`, `../services/mcp/types.js`, `../state/AppStateStore.js`, `../tools/AgentTool/loadAgentsDir.js`, `../types/message.js`, `./abortController.js`, `./fileStateCache.js`

**Main flow:** Entry: `buildSideQuestionFallbackParams()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/QueryGuard.ts` (121 lines)

**Exports:**
- `QueryGuard`

**Dependencies:** `./signal.js`

**Main flow:** Entry: `QueryGuard()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/queryHelpers.ts` (552 lines)

**Exports:**
- `PermissionPromptTool`
- `extractBashToolsFromMessages`
- `extractReadFilesFromMessages`
- `isResultSuccessful`

**Dependencies:** `../Tool.js`, `../hooks/useCanUseTool.js`, `../services/tools/toolOrchestration.js`, `../tools/BashTool/toolName.js`, `../tools/FileEditTool/constants.js`, `../tools/FileReadTool/FileReadTool.js`, `../tools/FileReadTool/prompt.js`, `../tools/FileWriteTool/prompt.js`, `../types/message.js`, `../types/textInputTypes.js`

**Main flow:** Entry: `isResultSuccessful()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/queryProfiler.ts` (301 lines)

**Exports:**
- `endQueryProfile`
- `logQueryProfileReport`
- `queryCheckpoint`
- `startQueryProfile`

**Dependencies:** `./debug.js`, `./envUtils.js`, `./profilerBase.js`

**Main flow:** Entry: `endQueryProfile()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/queueProcessor.ts` (95 lines)

**Exports:**
- `hasQueuedCommands`
- `processQueueIfReady`

**Dependencies:** `../types/textInputTypes.js`, `./messageQueueManager.js`

**Main flow:** Entry: `hasQueuedCommands()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/readEditContext.ts` (227 lines)

**Exports:**
- `CHUNK_SIZE`
- `EditContext`
- `MAX_SCAN_BYTES`
- `openForScan`
- `readCapped`
- `readEditContext`
- `scanForContext`

**Dependencies:** `./errors.js`

**Main flow:** Entry: `CHUNK_SIZE()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/readFileInRange.ts` (383 lines)

**Exports:**
- `FileTooLargeError`
- `ReadFileRangeResult`
- `readFileInRange`

**Dependencies:** `./format.js`

**Main flow:** Entry: `FileTooLargeError()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/releaseNotes.ts` (360 lines)

**Exports:**
- `CHANGELOG_URL`
- `_resetChangelogCacheForTesting`
- `checkForReleaseNotes`
- `checkForReleaseNotesSync`
- `fetchAndStoreChangelog`
- `getAllReleaseNotes`
- `getRecentReleaseNotes`
- `getStoredChangelog`
- `getStoredChangelogFromMemory`
- `migrateChangelogFromConfig`
- `parseChangelog`

**Dependencies:** `../bootstrap/state.js`, `./config.js`, `./envUtils.js`, `./errors.js`, `./log.js`, `./privacyLevel.js`, `./semver.js`

**Main flow:** Entry: `getAllReleaseNotes()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/renderOptions.ts` (77 lines)

**Exports:**
- `getBaseRenderOptions`

**Dependencies:** `../ink.js`, `./envUtils.js`, `./log.js`

**Main flow:** Entry: `getBaseRenderOptions()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/ripgrep.ts` (679 lines)

**Exports:**
- `RipgrepTimeoutError`
- `countFilesRoundedRg`
- `getRipgrepStatus`
- `ripGrep`
- `ripGrepStream`
- `ripgrepCommand`

**Dependencies:** `./bundledMode.js`, `./debug.js`, `./envUtils.js`, `./execFileNoThrow.js`, `./findExecutable.js`, `./log.js`, `./platform.js`, `./stringUtils.js`

**Main flow:** Entry: `getRipgrepStatus()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/sanitization.ts` (91 lines)

**Exports:**
- `partiallySanitizeUnicode`
- `recursivelySanitizeUnicode`

**Dependencies:** local only

**Main flow:** Entry: `partiallySanitizeUnicode()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/screenshotClipboard.ts` (121 lines)

**Exports:**
- `copyAnsiToClipboard`

**Dependencies:** `./ansiToPng.js`, `./execFileNoThrow.js`, `./log.js`, `./platform.js`

**Main flow:** Entry: `copyAnsiToClipboard()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/sdkEventQueue.ts` (134 lines)

**Exports:**
- `SdkEvent`
- `drainSdkEvents`
- `emitTaskTerminatedSdk`
- `enqueueSdkEvent`

**Dependencies:** `../bootstrap/state.js`, `../types/tools.js`

**Main flow:** Entry: `SdkEvent()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/semanticBoolean.ts` (29 lines)

**Exports:**
- `semanticBoolean`

**Dependencies:** local only

**Main flow:** Entry: `semanticBoolean()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/semanticNumber.ts` (36 lines)

**Exports:**
- `semanticNumber`

**Dependencies:** local only

**Main flow:** Entry: `semanticNumber()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/semver.ts` (59 lines)

**Exports:**
- `gt`
- `gte`
- `lt`
- `lte`
- `order`
- `satisfies`

**Dependencies:** local only

**Main flow:** Entry: `gt()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/sequential.ts` (56 lines)

**Exports:**
- `sequential`

**Dependencies:** local only

**Main flow:** Entry: `sequential()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/sessionActivity.ts` (133 lines)

**Exports:**
- `SessionActivityReason`
- `isSessionActivityTrackingActive`
- `registerSessionActivityCallback`
- `sendSessionActivitySignal`
- `startSessionActivity`
- `stopSessionActivity`
- `unregisterSessionActivityCallback`

**Dependencies:** `./cleanupRegistry.js`, `./diagLogs.js`, `./envUtils.js`

**Main flow:** Entry: `isSessionActivityTrackingActive()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/sessionEnvironment.ts` (166 lines)

**Exports:**
- `clearCwdEnvFiles`
- `getHookEnvFilePath`
- `getSessionEnvDirPath`
- `getSessionEnvironmentScript`
- `invalidateSessionEnvCache`

**Dependencies:** `../bootstrap/state.js`, `./debug.js`, `./envUtils.js`, `./errors.js`, `./platform.js`

**Main flow:** Entry: `getHookEnvFilePath()`

**Behavior:** Hook lifecycle helper; registers callbacks or dispatches hook events.

## `utils/sessionEnvVars.ts` (22 lines)

**Exports:**
- `clearSessionEnvVars`
- `deleteSessionEnvVar`
- `getSessionEnvVars`
- `setSessionEnvVar`

**Dependencies:** local only

**Main flow:** Entry: `getSessionEnvVars()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/sessionFileAccessHooks.ts` (250 lines)

**Exports:**
- `isMemoryFileAccess`
- `registerSessionFileAccessHooks`

**Dependencies:** `../bootstrap/state.js`, `../entrypoints/agentSdkTypes.js`, `../services/analytics/index.js`, `../tools/FileEditTool/constants.js`, `../tools/FileEditTool/types.js`, `../tools/FileReadTool/FileReadTool.js`, `../tools/FileReadTool/prompt.js`, `../tools/FileWriteTool/FileWriteTool.js`, `../tools/FileWriteTool/prompt.js`, `../tools/GlobTool/GlobTool.js`

**Feature gates:** `MEMORY_SHAPE_TELEMETRY`, `TEAMMEM`

**Main flow:** Entry: `isMemoryFileAccess()`

**Behavior:** Hook lifecycle helper; registers callbacks or dispatches hook events.

## `utils/sessionIngressAuth.ts` (140 lines)

**Exports:**
- `getSessionIngressAuthHeaders`
- `getSessionIngressAuthToken`
- `updateSessionIngressAuthToken`

**Dependencies:** `../bootstrap/state.js`, `./authFileDescriptor.js`, `./debug.js`, `./errors.js`, `./fsOperations.js`

**Main flow:** Entry: `getSessionIngressAuthHeaders()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/sessionRestore.ts` (551 lines)

**Exports:**
- `ProcessedResume`
- `computeRestoredAttributionState`
- `computeStandaloneAgentContext`
- `exitRestoredWorktree`
- `processResumedConversation`
- `refreshAgentDefinitionsForModeSwitch`
- `restoreAgentFromSession`
- `restoreSessionStateFromLog`
- `restoreWorktreeForResume`

**Dependencies:** `../bootstrap/state.js`, `../constants/systemPromptSections.js`, `../cost-tracker.js`, `../state/AppState.js`, `../tools/AgentTool/agentColorManager.js`, `../tools/AgentTool/loadAgentsDir.js`, `../tools/TodoWriteTool/constants.js`, `../types/ids.js`, `../types/logs.js`, `../types/message.js`

**Feature gates:** `COMMIT_ATTRIBUTION`, `CONTEXT_COLLAPSE`, `COORDINATOR_MODE`

**Main flow:** Entry: `ProcessedResume()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/sessionStart.ts` (232 lines)

**Exports:**
- `processSessionStartHooks`
- `processSetupHooks`
- `takeInitialUserMessage`

**Dependencies:** `../bootstrap/state.js`, `../types/message.js`, `./attachments.js`, `./debug.js`, `./diagLogs.js`, `./envUtils.js`, `./hooks.js`, `./hooks/fileChangedWatcher.js`, `./hooks/hooksConfigSnapshot.js`, `./log.js`

**Main flow:** Entry: `processSessionStartHooks()`

**Behavior:** Hook lifecycle helper; registers callbacks or dispatches hook events.

## `utils/sessionState.ts` (150 lines)

**Exports:**
- `RequiresActionDetails`
- `SessionExternalMetadata`
- `SessionState`
- `getSessionState`
- `notifyPermissionModeChanged`
- `notifySessionMetadataChanged`
- `notifySessionStateChanged`
- `setPermissionModeChangedListener`
- `setSessionMetadataChangedListener`
- `setSessionStateChangedListener`

**Dependencies:** `./envUtils.js`, `./permissions/PermissionMode.js`, `./sdkEventQueue.js`

**Main flow:** Entry: `getSessionState()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/sessionStoragePortable.ts` (793 lines)

**Exports:**
- `LITE_READ_BUF_SIZE`
- `LiteSessionFile`
- `MAX_SANITIZED_LENGTH`
- `SKIP_PRECOMPACT_THRESHOLD`
- `canonicalizePath`
- `extractFirstPromptFromHead`
- `extractJsonStringField`
- `extractLastJsonStringField`
- `findProjectDir`
- `getProjectDir`
- `getProjectsDir`
- `readHeadAndTail`
- `readSessionLite`
- `readTranscriptForLoad`
- `resolveSessionFilePath`
- `sanitizePath`
- `unescapeJsonString`
- `validateUuid`

**Dependencies:** `./envUtils.js`, `./getWorktreePathsPortable.js`, `./hash.js`

**Main flow:** Entry: `getProjectDir()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/sessionTitle.ts` (129 lines)

**Exports:**
- `extractConversationText`
- `generateSessionTitle`

**Dependencies:** `../bootstrap/state.js`, `../services/analytics/index.js`, `../services/api/claude.js`, `../types/message.js`, `./debug.js`, `./json.js`, `./lazySchema.js`, `./messages.js`, `./systemPromptType.js`

**Main flow:** Entry: `extractConversationText()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/sessionUrl.ts` (64 lines)

**Exports:**
- `ParsedSessionUrl`
- `parseSessionIdentifier`

**Dependencies:** `./uuid.js`

**Main flow:** Entry: `parseSessionIdentifier()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/set.ts` (53 lines)

**Exports:**
- `difference`
- `every`
- `intersects`
- `union`

**Dependencies:** local only

**Main flow:** Entry: `difference()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/Shell.ts` (474 lines)

**Exports:**
- `ExecOptions`
- `ExecResult`
- `ShellConfig`
- `exec`
- `findSuitableShell`
- `getPsProvider`
- `getShellConfig`
- `setCwd`

**Dependencies:** `../Task.js`, `../bootstrap/state.js`, `./ShellCommand.js`, `./cwd.js`, `./debug.js`, `./errors.js`, `./fsOperations.js`, `./hooks/fileChangedWatcher.js`, `./log.js`, `./permissions/filesystem.js`

**Main flow:** Entry: `getPsProvider()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/ShellCommand.ts` (465 lines)

**Exports:**
- `ExecResult`
- `ShellCommand`
- `createAbortedCommand`
- `createFailedCommand`
- `wrapSpawn`

**Dependencies:** `../Task.js`, `./format.js`, `./task/TaskOutput.js`, `./task/diskOutput.js`

**Main flow:** Entry: `createAbortedCommand()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/shellConfig.ts` (167 lines)

**Exports:**
- `CLAUDE_ALIAS_REGEX`
- `filterClaudeAliases`
- `findClaudeAlias`
- `findValidClaudeAlias`
- `getShellConfigPaths`
- `readFileLines`
- `writeFileLines`

**Dependencies:** `./errors.js`, `./localInstaller.js`

**Main flow:** Entry: `getShellConfigPaths()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/sideQuery.ts` (222 lines)

**Exports:**
- `SideQueryOptions`
- `sideQuery`

**Dependencies:** `../bootstrap/state.js`, `../constants/betas.js`, `../constants/querySource.js`, `../constants/system.js`, `../services/analytics/index.js`, `../services/analytics/metadata.js`, `../services/api/claude.js`, `../services/api/client.js`, `./betas.js`, `./fingerprint.js`

**Main flow:** Entry: `SideQueryOptions()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/sideQuestion.ts` (155 lines)

**Exports:**
- `SideQuestionResult`
- `findBtwTriggerPositions`
- `runSideQuestion`

**Dependencies:** `../services/api/errorUtils.js`, `../services/api/logging.js`, `../types/message.js`, `./forkedAgent.js`, `./messages.js`

**Main flow:** Entry: `SideQuestionResult()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/signal.ts` (43 lines)

**Exports:**
- `Signal`
- `createSignal`

**Dependencies:** local only

**Main flow:** Entry: `createSignal()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/sinks.ts` (16 lines)

**Exports:**
- `initSinks`

**Dependencies:** `../services/analytics/sink.js`, `./errorLogSink.js`

**Main flow:** Entry: `initSinks()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/slashCommandParsing.ts` (60 lines)

**Exports:**
- `ParsedSlashCommand`
- `parseSlashCommand`

**Dependencies:** local only

**Main flow:** Entry: `parseSlashCommand()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/sleep.ts` (84 lines)

**Exports:**
- `sleep`
- `withTimeout`

**Dependencies:** local only

**Main flow:** Entry: `sleep()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/sliceAnsi.ts` (91 lines)

**Exports:**
- (none)

**Dependencies:** `../ink/stringWidth.js`

**Main flow:** Entry: N/A

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/slowOperations.ts` (286 lines)

**Exports:**
- `callerFrame`
- `clone`
- `cloneDeep`
- `jsonParse`
- `jsonStringify`
- `slowLogging`
- `writeFileSync_DEPRECATED`

**Dependencies:** `../bootstrap/state.js`, `./debug.js`

**Feature gates:** `SLOW_OPERATION_LOGGING`

**Main flow:** Entry: `callerFrame()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/standaloneAgent.ts` (23 lines)

**Exports:**
- `getStandaloneAgentName`

**Dependencies:** `../state/AppState.js`, `./teammate.js`

**Main flow:** Entry: `getStandaloneAgentName()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/stats.ts` (1061 lines)

**Exports:**
- `ClaudeCodeStats`
- `DailyActivity`
- `DailyModelTokens`
- `SessionStats`
- `StatsDateRange`
- `StreakInfo`
- `aggregateClaudeCodeStats`
- `aggregateClaudeCodeStatsForRange`
- `readSessionStartDate`

**Dependencies:** `../types/logs.js`, `./debug.js`, `./errors.js`, `./fsOperations.js`, `./json.js`, `./messages.js`, `./sessionStorage.js`, `./shell/shellToolUtils.js`, `./slowOperations.js`, `./statsCache.js`

**Feature gates:** `SHOT_STATS`

**Main flow:** Entry: `ClaudeCodeStats()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/statsCache.ts` (434 lines)

**Exports:**
- `PersistedStatsCache`
- `STATS_CACHE_VERSION`
- `getStatsCachePath`
- `getTodayDateString`
- `getYesterdayDateString`
- `isDateBefore`
- `loadStatsCache`
- `mergeCacheWithNewStats`
- `saveStatsCache`
- `toDateString`
- `withStatsCacheLock`

**Dependencies:** `../entrypoints/agentSdkTypes.js`, `./debug.js`, `./envUtils.js`, `./errors.js`, `./fsOperations.js`, `./log.js`, `./slowOperations.js`, `./stats.js`

**Feature gates:** `SHOT_STATS`

**Main flow:** Entry: `isDateBefore()`

**Behavior:** In-memory or disk-backed cache with TTL/invalidation semantics.

## `utils/statusNoticeHelpers.ts` (20 lines)

**Exports:**
- `AGENT_DESCRIPTIONS_THRESHOLD`
- `getAgentDescriptionsTotalTokens`

**Dependencies:** `../services/tokenEstimation.js`, `../tools/AgentTool/loadAgentsDir.js`

**Main flow:** Entry: `getAgentDescriptionsTotalTokens()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/stream.ts` (76 lines)

**Exports:**
- `Stream`

**Dependencies:** local only

**Main flow:** Entry: `Stream()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/streamJsonStdoutGuard.ts` (123 lines)

**Exports:**
- `STDOUT_GUARD_MARKER`
- `_resetStreamJsonStdoutGuardForTesting`
- `installStreamJsonStdoutGuard`

**Dependencies:** `./cleanupRegistry.js`, `./debug.js`

**Main flow:** Entry: `STDOUT_GUARD_MARKER()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/streamlinedTransform.ts` (201 lines)

**Exports:**
- `createStreamlinedTransformer`
- `shouldIncludeInStreamlined`

**Dependencies:** local only

**Main flow:** Entry: `createStreamlinedTransformer()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/subprocessEnv.ts` (99 lines)

**Exports:**
- `registerUpstreamProxyEnvFn`
- `subprocessEnv`

**Dependencies:** `./envUtils.js`

**Main flow:** Entry: `registerUpstreamProxyEnvFn()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/systemDirectories.ts` (74 lines)

**Exports:**
- `SystemDirectories`
- `getSystemDirectories`

**Dependencies:** `./debug.js`, `./platform.js`

**Main flow:** Entry: `getSystemDirectories()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/systemPrompt.ts` (123 lines)

**Exports:**
- `buildEffectiveSystemPrompt`

**Dependencies:** `../Tool.js`, `../services/analytics/index.js`, `../tools/AgentTool/loadAgentsDir.js`, `./envUtils.js`, `./systemPromptType.js`

**Feature gates:** `COORDINATOR_MODE`, `KAIROS`, `PROACTIVE`

**Main flow:** Entry: `buildEffectiveSystemPrompt()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/systemPromptType.ts` (14 lines)

**Exports:**
- `SystemPrompt`
- `asSystemPrompt`

**Dependencies:** local only

**Main flow:** Entry: `SystemPrompt()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/systemTheme.ts` (119 lines)

**Exports:**
- `SystemTheme`
- `getSystemThemeName`
- `resolveThemeSetting`
- `setCachedSystemTheme`
- `themeFromOscColor`

**Dependencies:** `./theme.js`

**Main flow:** Entry: `getSystemThemeName()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/taggedId.ts` (54 lines)

**Exports:**
- `toTaggedId`

**Dependencies:** local only

**Main flow:** Entry: `toTaggedId()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/tasks.ts` (862 lines)

**Exports:**
- `AgentStatus`
- `ClaimTaskOptions`
- `ClaimTaskResult`
- `DEFAULT_TASKS_MODE_TASK_LIST_ID`
- `TASK_STATUSES`
- `Task`
- `TaskSchema`
- `TaskStatus`
- `TaskStatusSchema`
- `TeamMember`
- `UnassignTasksResult`
- `blockTask`
- `claimTask`
- `clearLeaderTeamName`
- `createTask`
- `deleteTask`
- `ensureTasksDir`
- `getAgentStatuses`
- `getTask`
- `getTaskListId`
- `getTaskPath`
- `getTasksDir`
- `isTodoV2Enabled`
- `listTasks`
- `notifyTasksUpdated`
- ... +6 more

**Dependencies:** `../bootstrap/state.js`, `./array.js`, `./debug.js`, `./envUtils.js`, `./errors.js`, `./lazySchema.js`, `./log.js`, `./signal.js`, `./slowOperations.js`, `./teammate.js`

**Main flow:** Entry: `isTodoV2Enabled()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/teamDiscovery.ts` (81 lines)

**Exports:**
- `TeamSummary`
- `TeammateStatus`
- `getTeammateStatuses`

**Dependencies:** `./swarm/backends/types.js`, `./swarm/teamHelpers.js`

**Main flow:** Entry: `getTeammateStatuses()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/teammate.ts` (292 lines)

**Exports:**
- `clearDynamicTeamContext`
- `getAgentId`
- `getAgentName`
- `getDynamicTeamContext`
- `getParentSessionId`
- `getTeamName`
- `getTeammateColor`
- `hasActiveInProcessTeammates`
- `hasWorkingInProcessTeammates`
- `isPlanModeRequired`
- `isTeamLead`
- `isTeammate`
- `setDynamicTeamContext`
- `waitForTeammatesToBecomeIdle`

**Dependencies:** `../state/AppState.js`, `./envUtils.js`, `./teammateContext.js`

**Main flow:** Entry: `isPlanModeRequired()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/teammateContext.ts` (96 lines)

**Exports:**
- `TeammateContext`
- `createTeammateContext`
- `getTeammateContext`
- `isInProcessTeammate`
- `runWithTeammateContext`

**Dependencies:** local only

**Main flow:** Entry: `isInProcessTeammate()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/teammateMailbox.ts` (1183 lines)

**Exports:**
- `IdleNotificationMessage`
- `ModeSetRequestMessage`
- `ModeSetRequestMessageSchema`
- `PermissionRequestMessage`
- `PermissionResponseMessage`
- `PlanApprovalRequestMessage`
- `PlanApprovalRequestMessageSchema`
- `PlanApprovalResponseMessage`
- `PlanApprovalResponseMessageSchema`
- `SandboxPermissionRequestMessage`
- `SandboxPermissionResponseMessage`
- `ShutdownApprovedMessage`
- `ShutdownApprovedMessageSchema`
- `ShutdownRejectedMessage`
- `ShutdownRejectedMessageSchema`
- `ShutdownRequestMessage`
- `ShutdownRequestMessageSchema`
- `TaskAssignmentMessage`
- `TeamPermissionUpdateMessage`
- `TeammateMessage`
- `clearMailbox`
- `createIdleNotification`
- `createModeSetRequestMessage`
- `createPermissionRequestMessage`
- `createPermissionResponseMessage`
- ... +29 more

**Dependencies:** `../constants/xml.js`, `../entrypoints/sdk/coreSchemas.js`, `../tools/SendMessageTool/constants.js`, `../types/message.js`, `./agentId.js`, `./array.js`, `./debug.js`, `./envUtils.js`, `./errors.js`, `./lazySchema.js`

**Main flow:** Entry: `isIdleNotification()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/teamMemoryOps.ts` (88 lines)

**Exports:**
- `appendTeamMemorySummaryParts`
- `isTeamMemorySearch`
- `isTeamMemoryWriteOrEdit`

**Dependencies:** `../memdir/teamMemPaths.js`, `../tools/FileEditTool/constants.js`, `../tools/FileWriteTool/prompt.js`

**Main flow:** Entry: `isTeamMemorySearch()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/telemetryAttributes.ts` (71 lines)

**Exports:**
- `getTelemetryAttributes`

**Dependencies:** `./auth.js`, `./config.js`, `./envDynamic.js`, `./envUtils.js`, `./taggedId.js`

**Main flow:** Entry: `getTelemetryAttributes()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/tempfile.ts` (31 lines)

**Exports:**
- `generateTempFilePath`

**Dependencies:** local only

**Main flow:** Entry: `generateTempFilePath()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/terminal.ts` (131 lines)

**Exports:**
- `isOutputLineTruncated`
- `renderTruncatedContent`

**Dependencies:** `../components/CtrlOToExpand.js`, `../ink/stringWidth.js`, `./sliceAnsi.js`

**Main flow:** Entry: `isOutputLineTruncated()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/terminalPanel.ts` (191 lines)

**Exports:**
- `getTerminalPanel`
- `getTerminalPanelSocket`

**Dependencies:** `../bootstrap/state.js`, `../ink/instances.js`, `./cleanupRegistry.js`, `./cwd.js`, `./debug.js`

**Main flow:** Entry: `getTerminalPanel()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/textHighlighting.ts` (166 lines)

**Exports:**
- `TextHighlight`
- `TextSegment`
- `segmentTextByHighlights`

**Dependencies:** `./theme.js`

**Main flow:** Entry: `TextHighlight()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/theme.ts` (639 lines)

**Exports:**
- `THEME_NAMES`
- `THEME_SETTINGS`
- `Theme`
- `ThemeName`
- `ThemeSetting`
- `getTheme`
- `themeColorToAnsi`

**Dependencies:** `./env.js`

**Main flow:** Entry: `getTheme()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/thinking.ts` (162 lines)

**Exports:**
- `ThinkingConfig`
- `findThinkingTriggerPositions`
- `getRainbowColor`
- `hasUltrathinkKeyword`
- `isUltrathinkEnabled`
- `modelSupportsAdaptiveThinking`
- `modelSupportsThinking`
- `shouldEnableThinkingByDefault`

**Dependencies:** `../services/analytics/growthbook.js`, `./model/model.js`, `./model/modelSupportOverrides.js`, `./model/providers.js`, `./settings/settings.js`, `./theme.js`

**Feature gates:** `ULTRATHINK`

**Main flow:** Entry: `isUltrathinkEnabled()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/timeouts.ts` (39 lines)

**Exports:**
- `getDefaultBashTimeoutMs`
- `getMaxBashTimeoutMs`

**Dependencies:** local only

**Main flow:** Entry: `getDefaultBashTimeoutMs()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/tmuxSocket.ts` (427 lines)

**Exports:**
- `checkTmuxAvailable`
- `ensureSocketInitialized`
- `getClaudeSocketName`
- `getClaudeSocketPath`
- `getClaudeTmuxEnv`
- `hasTmuxToolBeenUsed`
- `isSocketInitialized`
- `isTmuxAvailable`
- `markTmuxToolUsed`
- `resetSocketState`
- `setClaudeSocketInfo`

**Dependencies:** `./cleanupRegistry.js`, `./debug.js`, `./errors.js`, `./execFileNoThrow.js`, `./log.js`, `./platform.js`

**Main flow:** Entry: `isSocketInitialized()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/tokenBudget.ts` (73 lines)

**Exports:**
- `findTokenBudgetPositions`
- `getBudgetContinuationMessage`
- `parseTokenBudget`

**Dependencies:** local only

**Main flow:** Entry: `getBudgetContinuationMessage()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/tokens.ts` (261 lines)

**Exports:**
- `doesMostRecentAssistantMessageExceed200k`
- `finalContextTokensFromLastResponse`
- `getAssistantMessageContentLength`
- `getCurrentUsage`
- `getTokenCountFromUsage`
- `getTokenUsage`
- `messageTokenCountFromLastAPIResponse`
- `tokenCountFromLastAPIResponse`
- `tokenCountWithEstimation`

**Dependencies:** `../services/tokenEstimation.js`, `../types/message.js`, `./messages.js`, `./slowOperations.js`

**Main flow:** Entry: `getAssistantMessageContentLength()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/toolErrors.ts` (132 lines)

**Exports:**
- `formatError`
- `formatZodValidationError`
- `getErrorParts`

**Dependencies:** `./errors.js`, `./messages.js`

**Main flow:** Entry: `getErrorParts()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/toolPool.ts` (79 lines)

**Exports:**
- `applyCoordinatorToolFilter`
- `isPrActivitySubscriptionTool`
- `mergeAndFilterTools`

**Dependencies:** `../Tool.js`, `../constants/tools.js`, `../services/mcp/utils.js`

**Feature gates:** `COORDINATOR_MODE`

**Main flow:** Entry: `isPrActivitySubscriptionTool()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/toolResultStorage.ts` (1040 lines)

**Exports:**
- `ContentReplacementRecord`
- `ContentReplacementState`
- `PERSISTED_OUTPUT_CLOSING_TAG`
- `PERSISTED_OUTPUT_TAG`
- `PREVIEW_SIZE_BYTES`
- `PersistToolResultError`
- `PersistedToolResult`
- `TOOL_RESULTS_SUBDIR`
- `TOOL_RESULT_CLEARED_MESSAGE`
- `ToolResultReplacementRecord`
- `applyToolResultBudget`
- `buildLargeToolResultMessage`
- `cloneContentReplacementState`
- `createContentReplacementState`
- `enforceToolResultBudget`
- `ensureToolResultsDir`
- `generatePreview`
- `getPerMessageBudgetLimit`
- `getPersistenceThreshold`
- `getToolResultPath`
- `getToolResultsDir`
- `isPersistError`
- `isToolResultContentEmpty`
- `persistToolResult`
- `processPreMappedToolResultBlock`
- ... +4 more

**Dependencies:** `../bootstrap/state.js`, `../constants/toolLimits.js`, `../services/analytics/growthbook.js`, `../services/analytics/index.js`, `../services/analytics/metadata.js`, `../types/message.js`, `./debug.js`, `./errors.js`, `./format.js`, `./log.js`

**Feature gates:** `TRANSCRIPT_CLASSIFIER`

**Main flow:** Entry: `isPersistError()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/toolSchemaCache.ts` (26 lines)

**Exports:**
- `clearToolSchemaCache`
- `getToolSchemaCache`

**Dependencies:** local only

**Main flow:** Entry: `getToolSchemaCache()`

**Behavior:** In-memory or disk-backed cache with TTL/invalidation semantics.

## `utils/toolSearch.ts` (756 lines)

**Exports:**
- `DeferredToolsDelta`
- `DeferredToolsDeltaScanContext`
- `ToolSearchMode`
- `extractDiscoveredToolNames`
- `getAutoToolSearchCharThreshold`
- `getDeferredToolsDelta`
- `getToolSearchMode`
- `isDeferredToolsDeltaEnabled`
- `isToolReferenceBlock`
- `isToolSearchEnabled`
- `isToolSearchEnabledOptimistic`
- `isToolSearchToolAvailable`
- `modelSupportsToolReference`

**Dependencies:** `../Tool.js`, `../services/analytics/growthbook.js`, `../services/analytics/index.js`, `../tools/AgentTool/loadAgentsDir.js`, `../tools/ToolSearchTool/prompt.js`, `../types/message.js`, `./analyzeContext.js`, `./array.js`, `./betas.js`, `./context.js`

**Main flow:** Entry: `isDeferredToolsDeltaEnabled()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/transcriptSearch.ts` (202 lines)

**Exports:**
- `renderableSearchText`
- `toolResultSearchText`
- `toolUseSearchText`

**Dependencies:** `../types/message.js`, `./messages.js`

**Main flow:** Entry: `renderableSearchText()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/treeify.ts` (170 lines)

**Exports:**
- `TreeNode`
- `TreeifyOptions`
- `treeify`

**Dependencies:** `../components/design-system/color.js`, `./theme.js`

**Main flow:** Entry: `TreeNode()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/truncate.ts` (179 lines)

**Exports:**
- `truncate`
- `truncatePathMiddle`
- `truncateStartToWidth`
- `truncateToWidth`
- `truncateToWidthNoEllipsis`
- `wrapText`

**Dependencies:** `../ink/stringWidth.js`, `./intl.js`

**Main flow:** Entry: `truncate()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/unaryLogging.ts` (39 lines)

**Exports:**
- `CompletionType`
- `logUnaryEvent`

**Dependencies:** local only

**Main flow:** Entry: `CompletionType()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/undercover.ts` (89 lines)

**Exports:**
- `getUndercoverInstructions`
- `isUndercover`
- `shouldShowUndercoverAutoNotice`

**Dependencies:** `./commitAttribution.js`, `./config.js`, `./envUtils.js`

**Main flow:** Entry: `isUndercover()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/user.ts` (194 lines)

**Exports:**
- `CoreUserData`
- `GitHubActionsMetadata`
- `getCoreUserData`
- `getGitEmail`
- `getUserForGrowthBook`
- `initUser`
- `resetUserCache`

**Dependencies:** `../bootstrap/state.js`, `./auth.js`, `./config.js`, `./cwd.js`, `./env.js`, `./envUtils.js`

**Main flow:** Entry: `getCoreUserData()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/userAgent.ts` (10 lines)

**Exports:**
- `getClaudeCodeUserAgent`

**Dependencies:** local only

**Main flow:** Entry: `getClaudeCodeUserAgent()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/userPromptKeywords.ts` (27 lines)

**Exports:**
- `matchesKeepGoingKeyword`
- `matchesNegativeKeyword`

**Dependencies:** local only

**Main flow:** Entry: `matchesKeepGoingKeyword()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/uuid.ts` (27 lines)

**Exports:**
- `createAgentId`
- `validateUuid`

**Dependencies:** local only

**Main flow:** Entry: `createAgentId()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/warningHandler.ts` (121 lines)

**Exports:**
- `MAX_WARNING_KEYS`
- `initializeWarningHandler`
- `resetWarningHandler`

**Dependencies:** `./debug.js`, `./envUtils.js`, `./platform.js`

**Main flow:** Entry: `initializeWarningHandler()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/which.ts` (82 lines)

**Exports:**
- `which`
- `whichSync`

**Dependencies:** `./execSyncWrapper.js`

**Main flow:** Entry: `which()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/windowsPaths.ts` (173 lines)

**Exports:**
- `findGitBashPath`
- `posixPathToWindowsPath`
- `setShellIfWindows`
- `windowsPathToPosixPath`

**Dependencies:** `./cwd.js`, `./debug.js`, `./execSyncWrapper.js`, `./memoize.js`, `./platform.js`

**Main flow:** Entry: `findGitBashPath()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/withResolvers.ts` (13 lines)

**Exports:**
- `withResolvers`

**Dependencies:** local only

**Main flow:** Entry: `withResolvers()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/words.ts` (800 lines)

**Exports:**
- `generateShortWordSlug`
- `generateWordSlug`

**Dependencies:** local only

**Main flow:** Entry: `generateShortWordSlug()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/workloadContext.ts` (57 lines)

**Exports:**
- `WORKLOAD_CRON`
- `Workload`
- `getWorkload`
- `runWithWorkload`

**Dependencies:** local only

**Main flow:** Entry: `getWorkload()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/worktree.ts` (1519 lines)

**Exports:**
- `WorktreeSession`
- `cleanupStaleAgentWorktrees`
- `cleanupWorktree`
- `copyWorktreeIncludeFiles`
- `createAgentWorktree`
- `createTmuxSessionForWorktree`
- `createWorktreeForSession`
- `execIntoTmuxWorktree`
- `generateTmuxSessionName`
- `getCurrentWorktreeSession`
- `getTmuxInstallInstructions`
- `hasWorktreeChanges`
- `isTmuxAvailable`
- `keepWorktree`
- `killTmuxSession`
- `parsePRReference`
- `removeAgentWorktree`
- `restoreWorktreeSession`
- `validateWorktreeSlug`
- `worktreeBranchName`

**Dependencies:** `./config.js`, `./cwd.js`, `./debug.js`, `./errors.js`, `./execFileNoThrow.js`, `./git.js`, `./git/gitConfigParser.js`, `./git/gitFilesystem.js`, `./hooks.js`, `./path.js`

**Feature gates:** `COMMIT_ATTRIBUTION`

**Main flow:** Entry: `isTmuxAvailable()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/worktreeModeEnabled.ts` (11 lines)

**Exports:**
- `isWorktreeModeEnabled`

**Dependencies:** local only

**Main flow:** Entry: `isWorktreeModeEnabled()`

**Behavior:** Type guard / feature probe used at call sites before branching.

## `utils/xdg.ts` (65 lines)

**Exports:**
- `getUserBinDir`
- `getXDGCacheHome`
- `getXDGDataHome`
- `getXDGStateHome`

**Dependencies:** local only

**Main flow:** Entry: `getUserBinDir()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/xml.ts` (16 lines)

**Exports:**
- `escapeXml`
- `escapeXmlAttr`

**Dependencies:** local only

**Main flow:** Entry: `escapeXml()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/yaml.ts` (15 lines)

**Exports:**
- `parseYaml`

**Dependencies:** local only

**Main flow:** Entry: `parseYaml()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

## `utils/zodToJsonSchema.ts` (23 lines)

**Exports:**
- `JsonSchema7Type`
- `zodToJsonSchema`

**Dependencies:** local only

**Main flow:** Entry: `JsonSchema7Type()`

**Behavior:** Module-level utilities and side effects; validates inputs at call sites.

---

# Part 2 — Subdirectory Behavior Gap Fill

Modules below are mentioned briefly in `07-utils-layer.md` §14 or omitted from `08-utils-hooks-task-subprocesses.md`. File names and behavior verified against source (Phase 1 audit).

## `utils/background/remote/` (2 files)

| File | Behavior |
|------|----------|
| `preconditions.ts` | Async precondition checks for remote/teleport flows: OAuth login, git cleanliness, remote environment availability, GitHub App install, org policy. |
| `remoteSession.ts` | `BackgroundRemoteSession` type and eligibility checks combining preconditions for background remote session spawn. |

## `utils/dxt/` (2 files)

| File | Behavior |
|------|----------|
| `helpers.ts` | Lazy-validates MCPB/DXT plugin manifests via `@anthropic-ai/mcpb` (deferred import to avoid startup zod cost). |
| `zip.ts` | Extracts `.dxt`/`.mcpb` plugin archives to temp dirs with manifest discovery. |

## `utils/filePersistence/` (2 files)

| File | Behavior |
|------|----------|
| `filePersistence.ts` | End-of-turn orchestrator: scans modified outputs, uploads via Files API (BYOC) or lists directory (cloud/rclone). |
| `outputsScanner.ts` | Mtime-based scanner for `outputs/` subtree; detects `EnvironmentKind` from env vars. |

## `utils/github/` (1 file)

| File | Behavior |
|------|----------|
| `ghAuthStatus.ts` | Non-blocking `gh` CLI probe (`which` + `gh auth token` exit code) for telemetry — never reads token stdout. |

## `utils/mcp/` (2 files)

| File | Behavior |
|------|----------|
| `elicitationValidation.ts` | Validates MCP elicitation form fields (string formats, enums, natural-language dates) before user submit. |
| `dateTimeParser.ts` | Parses natural-language and ISO-8601 datetime strings for MCP elicitation defaults. |

## `utils/memory/` (2 files)

| File | Behavior |
|------|----------|
| `versions.ts` | Sync git-repo probe via `findGitRoot` for memory feature gating. |
| `types.ts` | Memory record version enums and schema shapes for memdir persistence. |

## `utils/messages/` (2 files)

| File | Behavior |
|------|----------|
| `mappers.ts` | Maps SDK wire messages ↔ internal `Message[]` (assistant, compact boundaries, plan mode). |
| `systemInit.ts` | Builds SDK `system/init` and `result` init payloads; `sdkCompatToolName` Task→Agent shim. |

## `utils/todo/` (1 file)

| File | Behavior |
|------|----------|
| `types.ts` | `TodoList` / `TodoItem` shapes shared by tasks UI and background remote sessions. |

## `utils/ultraplan/` (2 files)

| File | Behavior |
|------|----------|
| `keyword.ts` | Detects `ultraplan` trigger keyword in user input with delimiter-aware parsing (skips quoted/backtick regions). |
| `ccrSession.ts` | CCR session helpers for ultraplan mode sync with remote worker metadata. |

## `utils/powershell/` (3 files)

| File | Behavior |
|------|----------|
| `parser.ts` | Invokes PowerShell AST parser (`System.Management.Automation.Language`) for security classification of cmdlets/pipelines. |
| `dangerousCmdlets.ts` | Blocklist/allowlist tables for high-risk PowerShell cmdlets used by permission checks. |
| `staticPrefix.ts` | Detects static command prefixes safe to auto-classify without full AST parse. |

## `utils/sandbox/` (2 files)

| File | Behavior |
|------|----------|
| `sandbox-adapter.ts` | `SandboxManager` interface — create/exec/teardown for containerized tool runs. |
| `sandbox-ui-utils.ts` | Status-line formatting for sandbox state in the REPL footer. |

## `utils/processUserInput/` (4 files)

| File | Behavior |
|------|----------|
| `processUserInput.ts` | Central input pipeline: slash commands, attachments, hooks, message assembly. |
| `processTextPrompt.ts` | Plain-text branch — skill expansion, @file refs, queue handoff. |
| `processSlashCommand.tsx` | `/command` dispatch to local/JSX/prompt command handlers. |
| `processBashCommand.tsx` | `!` / bash-prefixed command execution path. |
