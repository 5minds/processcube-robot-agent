import React from 'react';

import {
  BpmnDocumentModel,
  BpmnElementType,
  getUrlForOpenInNewTab,
  MultiLineCodeEditor,
  PaneBody,
  PaneComponentProps,
  PaneProperty,
  RuntimeExpressionHint,
} from '@atlas-engine/atlas_studio_sdk';
import { BpmnElement_ExternalServiceTask } from '@atlas-engine/atlas_studio_sdk/out/types/bpmn/BpmnElementTypes';
import { getRobotAgents, RobotAgent, RobotAgentSelectOption } from '../agentSettings/getRobotAgents';
import { fetchRobots, RobotSelectOption } from './fetchRobots';
import { ROBOT_AGENT_PROPERTY_NAME } from './initializeServiceTypeRobot';

type PaneContentProps = Omit<PaneComponentProps, 'editorDocumentModel'> & { editorDocumentModel: BpmnDocumentModel };
type PaneContentState = {
  declarationFiles: Array<string>;
  robotsForSelectedAgent: Array<RobotSelectOption>;
  selectedAgent: RobotAgent | null;
};

export class PropertiesRobotTaskPaneContent extends React.Component<PaneContentProps, PaneContentState> {
  constructor(props: PaneComponentProps) {
    super(props);

    this.state = {
      declarationFiles: [],
      robotsForSelectedAgent: [],
      selectedAgent: null,
    };

    props.studio.commands
      .executeCommand<Promise<string>>('bpmn.editor.getDefaultJavaScriptDeclarationFile', [props.editorDocument])
      .then(declarationFile => this.setState({ declarationFiles: [declarationFile] }));
  }

  private updateExternalTask(elementId: string, properties: Record<string, string>): void {
    this.props.editorDocumentModel.elements.setElementProperty(elementId, 'externalTask', properties);
  }

  private getRobotAgentSelectOptions(): Array<RobotAgentSelectOption> {
    const agents = getRobotAgents(this.props.studio)?.agents ?? [];
    const agentSelectOptions = agents.map(agent => ({
      label: agent.name,
      value: agent,
    }));
    return agentSelectOptions;
  }

  private findSelectedAgent(agents: Array<RobotAgentSelectOption>, selectedElement: BpmnElement_ExternalServiceTask): RobotAgentSelectOption | undefined {
    const selectedAgentId = selectedElement.customProperties
      ?.find(customProperty => customProperty.name === ROBOT_AGENT_PROPERTY_NAME)
      ?.value;

    if (selectedAgentId === undefined) {
      return undefined;
    }

    return agents.find(option => option.value.uuid === selectedAgentId) ?? {
      label: 'Unknown Agent',
      value: {
        uuid: selectedAgentId,
        url: '',
        name: '',
      },
    };
  }

  private getRobotsForAgent(agent: RobotAgentSelectOption | undefined): void {
    this.setState({ robotsForSelectedAgent: [], selectedAgent: agent?.value ?? null });
    if (agent === undefined) {
      return;
    }

    fetchRobots(agent.value.url, this.props.studio)
      .then(fetchedRobots => {
        const selectOptions: Array<RobotSelectOption> = fetchedRobots.map(robot => ({
          label: robot.name,
          value: robot,
        }));
        this.setState({ robotsForSelectedAgent: selectOptions });
      })
      .catch(error =>
        this.props.studio.notifications.open({
          content: `Could not fetch robots from '${agent.value.url}' due to: ${error}`,
          type: 'error',
        })
      );
  }

  private findSelectedRobot(element: BpmnElement_ExternalServiceTask): RobotSelectOption | undefined {
    const topic = element.topic;

    if (topic?.length === 0) {
      return undefined;
    }

    return this.state.robotsForSelectedAgent.find(robot => robot.value.topic === topic) ?? {
      label: 'Unknown Topic: ' + topic,
      value: {
        name: '',
        topic,
      },
    };
  }

  public render(): JSX.Element {
    const selectedElement = this.props.editorDocumentModel.selection.getOnlyElementOrNull();

    if (selectedElement === null || selectedElement.type !== BpmnElementType.ExternalServiceTask) {
      return <></>;
    }

    const agents = this.getRobotAgentSelectOptions();

    const selectedAgent = this.findSelectedAgent(agents, selectedElement as any);

    const selectedRobot = this.findSelectedRobot(selectedElement as any);

    if (selectedAgent?.value.uuid !== this.state.selectedAgent?.uuid) {
      this.getRobotsForAgent(selectedAgent);
    }

    return (
      <PaneBody>
        <div className='form-group'>
          <label className='d-block'>Agent</label>
          <PaneProperty
            key={JSON.stringify(selectedAgent)}
            type='select'
            options={agents}
            onChange={(option: RobotAgentSelectOption) => {
              this.props.editorDocumentModel.elements.setCustomProperty(selectedElement.id, ROBOT_AGENT_PROPERTY_NAME, option.value.uuid);
              this.getRobotsForAgent(option);
            }}
            value={selectedAgent}
          />
          <label className='d-block'>Topic</label>
          <PaneProperty
            key={JSON.stringify(selectedRobot)}
            type='select'
            options={this.state.robotsForSelectedAgent}
            onChange={(option: RobotSelectOption) => this.updateExternalTask(selectedElement.id, { topic: option.value.topic })}
            value={selectedRobot}
          />
          <label className="d-block">
            Body
            {' '}
            <small>
              <a
                href="#"
                onClick={() => this.props.studio.editors.focusOrOpenEditorDocument(getUrlForOpenInNewTab('bpmn.external-service-task.payload', this.props.editorDocument.uri, selectedElement.id))}
              >
                Open in new tab
              </a>
            </small>
            <RuntimeExpressionHint className="float-right" studio={this.props.studio} requiresInterpolation={false} />
          </label>
          <MultiLineCodeEditor
            className='pane__textarea'
            studio={this.props.studio}
            initialValue={(selectedElement as any).payload ?? ''}
            language='javascript'
            onChange={(value: string) => this.updateExternalTask(selectedElement.id, { payload: value })}
            declarationFiles={this.state.declarationFiles}
          />
        </div>
      </PaneBody>
    );
  }
}
