import * as vscode from "vscode";
import { buildAndSendEvent } from "../events/eventBuilder";

export async function initGitCollector(
  context: vscode.ExtensionContext
) {
  const gitExtension = vscode.extensions.getExtension("vscode.git");
  if (!gitExtension) {
    console.warn("[CareerStory] vscode.git extension not found");
    return;
  }

  // 🔑 REQUIRED
  await gitExtension.activate();

  const gitApi = gitExtension.exports.getAPI(1);
  if (!gitApi) {
    console.warn("[CareerStory] Git API not available");
    return;
  }

  gitApi.onDidChangeState(() => {
    const repo = gitApi.repositories[0];
    if (!repo) return;

    const staged = repo.state.indexChanges.length;
    const unstaged = repo.state.workingTreeChanges.length;
    const branch = repo.state.HEAD?.name;

    if (staged > 0) {
      buildAndSendEvent("pre_commit_intent", {
        branch,
        staged_files: staged,
        unstaged_files: unstaged,
      });
    }
  });
}
