import { Studio } from '@atlas-engine/atlas_studio_sdk';

import { initializeServiceTypeRobot } from './robotServiceType/initializeServiceTypeRobot';

export function onLoad(studio: Studio): void {
  initializeServiceTypeRobot(studio);

  // studio.menus.appendToMenu(studio.menus.getMenuSync('std/activity-bar/settings'), [{
  //   type: 'divider',
  // },{
  //   label: 'Robot Sources',
  //   command: 'std.shell.checkForStudioUpdate',
  //   type: 'command',
  //   id: 'std/activity-bar/settings/robot-sources',
  // }]);
}
