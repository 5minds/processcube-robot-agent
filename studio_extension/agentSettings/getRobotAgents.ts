import * as fs from 'fs';

import { SelectOption, Studio } from '@atlas-engine/atlas_studio_sdk';
import { WatcherDisposable } from '@atlas-engine/atlas_studio_sdk/out/types/common';

export type RobotAgent = {
  name: string;
  url: string;
  uuid: string;
};

export type RobotAgents = {
  agents: Array<RobotAgent>;
};

export type RobotAgentSelectOption = Omit<SelectOption, 'value'> & { value: RobotAgent };

export const SOLUTION_ROBOT_DIRECTORY = '/.processcube/robot-agent/';
export const AGENT_CONFIG_FILE_NAME = 'agents.json';

let robotAgentSettings: RobotAgents | null = null;
let watcher: WatcherDisposable | null = null;

export function getRobotAgents(studio: Studio): RobotAgents | null {
  if (watcher === null) {
    return registerFileWatcher(studio);
  }

  return robotAgentSettings;
}

function registerFileWatcher(studio: Studio): RobotAgents | null {
  const solutionURI = studio.solution.getSolution()?.baseUri;
  if (solutionURI === undefined) {
    return null;
  }

  const agentDirectory = studio.files.getLocalFilenameForUri(solutionURI + SOLUTION_ROBOT_DIRECTORY);
  const agentConfigFile = agentDirectory + AGENT_CONFIG_FILE_NAME;

  if (!fs.existsSync(agentConfigFile)) {
    createConfigFile(agentDirectory);
  }

  readAgentFile(agentConfigFile);

  watcher = studio.files.watchFile(
    studio.files.getUriForFilename(agentConfigFile),
    () => readAgentFile(agentConfigFile),
  );

  return robotAgentSettings;
}

function createConfigFile(agentDirectory: string) {
  fs.mkdirSync(agentDirectory, { recursive: true });
  fs.writeFileSync(agentDirectory + AGENT_CONFIG_FILE_NAME, JSON.stringify({ agents: [] }));
}

function readAgentFile(agentConfigFile: string): void {
  robotAgentSettings = JSON.parse(fs.readFileSync(agentConfigFile, 'utf8'));
}
