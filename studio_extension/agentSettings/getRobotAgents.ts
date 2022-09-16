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

export const ROBOT_AGENT_SOLUTION_DIR = '/.processcube/robot-agent/';
export const ROBOT_AGENT_CONFIG_FILE = ROBOT_AGENT_SOLUTION_DIR + 'agents.json';

let robotAgentSettings: RobotAgents | null = null;
let watcher: WatcherDisposable | null = null;

export function getRobotAgents(studio: Studio): RobotAgents | null {
  if (watcher !== null) {
    return robotAgentSettings;
  }

  const solutionURI = studio.solution.getSolution()?.baseUri;
  if (!solutionURI) {
    return robotAgentSettings;
  }

  const robotLocatorsFileName = studio.files.getLocalFilenameForUri(solutionURI) + ROBOT_AGENT_CONFIG_FILE;
  if (!fs.existsSync(robotLocatorsFileName)) {
    fs.mkdirSync(`${studio.files.getLocalFilenameForUri(solutionURI)}${ROBOT_AGENT_SOLUTION_DIR}`);
    fs.writeFileSync(robotLocatorsFileName, JSON.stringify({ agents: [] }));
  }

  robotAgentSettings = JSON.parse(fs.readFileSync(robotLocatorsFileName, 'utf8'));
  watcher = studio.files.watchFile(studio.files.getUriForFilename(robotLocatorsFileName), () => robotAgentSettings = JSON.parse(fs.readFileSync(robotLocatorsFileName, 'utf-8')));

  return robotAgentSettings;
}
