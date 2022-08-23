import React from 'react';

import { PaneComponentProps} from '@atlas-engine/atlas_studio_sdk';

import {
    Pane,
    PaneHeader,
    PaneHeaderHelpIcon,
} from '@atlas-engine/atlas_studio_sdk';
  
export function getRobotTaskPaneTitle(): string {
    return 'Robot Task';
}

export function RobotTaskPane(props: PaneComponentProps): JSX.Element {
    return (
      <Pane>
        <PaneHeader studio={props.studio} title={getRobotTaskPaneTitle()} paneId={props.paneId} collapsed={props.collapsed}>
          <PaneHeaderHelpIcon studio={props.studio} id="bpmn/properties/robot_task" />
        </PaneHeader>
        {props.collapsed !== true && <PaneContent {...props} />}
      </Pane>
    );
  }

  function PaneContent(props: PaneComponentProps): JSX.Element | null {
    const selection = null;
    
    if (selection == null) {
      return null;
    } else {
      return null;
    }
  }
  