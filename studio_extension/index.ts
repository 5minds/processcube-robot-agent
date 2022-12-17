import { Studio } from '@atlas-engine/atlas_studio_sdk';

import { initializeServiceTaskTypeRobot } from './robotServiceType/initializeServiceTypeRobot';
import { initializeAgentSettingsEditor } from './agentSettings/initializeAgentSettingsEditor';

export function onLoad(studio: Studio): void {
  initializeServiceTaskTypeRobot(studio);
  initializeAgentSettingsEditor(studio);
}
