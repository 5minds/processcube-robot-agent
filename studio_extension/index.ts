import fs from 'fs';
import { Studio } from '@atlas-engine/atlas_studio_sdk';

import {initializeRobotServiceTypePanel} from './initializePanes';
import {initializeServiceTypeRobot} from './initializeServiceTypeRobot';
import {initializeDefaultSettings} from './initializeStudioSettings';

export function onLoad(studio: Studio): void {
  initializeRobotServiceTypePanel(studio);
  initializeServiceTypeRobot(studio);
  initializeDefaultSettings(studio);
}
