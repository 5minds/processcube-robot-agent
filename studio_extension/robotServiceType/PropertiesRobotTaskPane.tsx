import React, { useState } from 'react';

import {
  BpmnDocumentModel,
  BpmnElementType,
  EditorDocument,
  EditorDocumentModel,
  getUrlForOpenInNewTab,
  MultiLineCodeEditor,
  Pane,
  PaneBody,
  PaneComponentProps,
  PaneHeader,
  PaneProperty,
  PaneProvider,
  RuntimeExpressionHint,
  SelectOption,
  Studio,
} from '@atlas-engine/atlas_studio_sdk';
import { getRobotAgents, RobotAgent, RobotAgentSelectOption } from '../agentSettings/getRobotAgents';
import { fetchRobots, RobotSelectOption } from './fetchTasks';
import { BpmnElement_ExternalServiceTask } from '@atlas-engine/atlas_studio_sdk/out/types/bpmn/BpmnElementTypes';

const robotAddinAgentIdPropertyName = 'studio.externalTask.robotAddin.agentId';

function shouldBeDisplayed(editorDocument: EditorDocument, editorDocumentModel: EditorDocumentModel, studio: Studio): boolean {
  if (editorDocument?.documentType !== 'bpmn') {
    return false;
  }

  const selectedElement = (editorDocumentModel as BpmnDocumentModel)?.selection?.getOnlyElementOrNull();

  const isExternalServiceTask = selectedElement?.type === BpmnElementType.ExternalServiceTask;

  if (!isExternalServiceTask) {
    return false;
  }

  const customExternalTaskType = selectedElement?.customProperties?.find(
    (customProperty) => customProperty.name === 'studio.externalTask.customType'
  )?.value;

  const isRobotExternalTask = customExternalTaskType === 'robot';

  return isRobotExternalTask;
}

function PaneFull(props: PaneComponentProps): JSX.Element {
  return (
    <Pane>
      <PaneHeader
        className='pane-header--hero'
        collapsed={props.collapsed}
        paneId={props.paneId}
        studio={props.studio}
        title='Robot Service Task'
      />
      {!props.collapsed &&
        <PaneContent {...props} />
      }
    </Pane>
  );
}

type PaneContentProps = Omit<PaneComponentProps, 'editorDocumentModel'> & { editorDocumentModel: BpmnDocumentModel };
type PaneContentState = {
  declarationFiles: Array<string>,
  invalidURLs: Array<string>,
  robotsForSelectedAgent: Array<RobotSelectOption>,
};

class PaneContent extends React.Component<PaneContentProps, PaneContentState> {
  constructor(props: PaneComponentProps) {
    super(props);

    this.state = {
      declarationFiles: [],
      invalidURLs: [],
      robotsForSelectedAgent: [],
    };

    props.studio.commands
    .executeCommand<Promise<string>>('bpmn.editor.getDefaultJavaScriptDeclarationFile', [props.editorDocument])
    .then((declarationFile) => {
      this.setState({ declarationFiles: [...this.state.declarationFiles, declarationFile] });
    });

    const selectedExternalTaskService = this.props.editorDocumentModel.selection.getOnlyElementOrNull();

    if (selectedExternalTaskService === null || selectedExternalTaskService.type !== BpmnElementType.ExternalServiceTask) {
      return;
    }

    const agents = this.getRobotAgentSelectOptions();

    const selectedAgent = this.findSelectedAgent(agents, selectedExternalTaskService as any);

    this.getRobotsForAgent(selectedAgent);
  }

  private updateExternalTask(id: string, externalTask: any): void {
    this.props.editorDocumentModel.elements.setElementProperty(id, 'externalTask', externalTask);
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
      ?.find(customProperty => customProperty.name === robotAddinAgentIdPropertyName)
      ?.value;
    const selectedAgent = agents.find(option => option.value.uuid === selectedAgentId);
    return selectedAgent
      ?? (selectedAgentId
        ? {
          label: 'Unknown Agent',
          value: {
            uuid: selectedAgentId ?? '',
            url: '',
            name: '',
          },
        }
        : undefined);
  }

  private getRobotsForAgent(agent: RobotAgentSelectOption | undefined): void {
    this.setState({ robotsForSelectedAgent: [] });
    if (agent === undefined) {
      return;
    }

    if (this.state.invalidURLs.includes(agent.value.url)) {
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
        this.setState({
          invalidURLs: [
            ...this.state.invalidURLs,
            agent.value.url
          ],
        },
        () =>
          this.props.studio.notifications.open({
            content: `Could not fetch robots from '${agent.value.url}' due to: ${error}`,
            type: 'error',
          })
        )
      );
  }

  private findSelectedRobot(robots: Array<RobotSelectOption>, element: BpmnElement_ExternalServiceTask): RobotSelectOption | undefined {
    const topic = element.topic;
    const selectedRobot = robots.find(robot => robot.value.topic === topic);
    return selectedRobot
      ?? (topic
        ? {
          label: 'Unknown Topic: ' + topic,
          value: {
            name: '',
            topic,
          },
        }
        : undefined
      );
  }

  public render(): JSX.Element {
    const selectedExternalTaskService = this.props.editorDocumentModel.selection.getOnlyElementOrNull();

    if (selectedExternalTaskService === null || selectedExternalTaskService.type !== BpmnElementType.ExternalServiceTask) {
      return <></>;
    }

    const agents = this.getRobotAgentSelectOptions();

    const selectedAgent = this.findSelectedAgent(agents, selectedExternalTaskService as any);

    const selectedRobot = this.findSelectedRobot(this.state.robotsForSelectedAgent, selectedExternalTaskService as any);

    return (
      <PaneBody>
        <div className='form-group'>
          <label className='d-block'>Agent</label>
          <PaneProperty
            type='select'
            options={agents}
            onChange={(option: RobotAgentSelectOption) => {
              this.props.editorDocumentModel.elements.setCustomProperty(selectedExternalTaskService.id, robotAddinAgentIdPropertyName, option.value.uuid);
              this.getRobotsForAgent(option);
            }}
            value={selectedAgent}
          />
          <label className='d-block'>Topic</label>
          <PaneProperty
            type='select'
            options={this.state.robotsForSelectedAgent}
            onChange={(option: RobotSelectOption) => this.updateExternalTask(selectedExternalTaskService.id, { topic: option.value.topic })}
            value={selectedRobot}
          />
          {JSON.stringify(selectedRobot)}
          <label className="d-block">
            Body
            {' '}
            <small>
              <a
                href="#"
                onClick={() => this.props.studio.editors.focusOrOpenEditorDocument(getUrlForOpenInNewTab('bpmn.external-service-task.payload', this.props.editorDocument.uri, selectedExternalTaskService.id))}
              >
                Open in new tab
              </a>
            </small>
            <RuntimeExpressionHint className="float-right" studio={this.props.studio} requiresInterpolation={false} />
          </label>
          <MultiLineCodeEditor
            className='pane__textarea'
            studio={this.props.studio}
            initialValue={(selectedExternalTaskService as any).payload ?? ''}
            language='javascript'
            onChange={(value: string) => this.updateExternalTask(selectedExternalTaskService.id, { payload: value })}
            declarationFiles={this.state.declarationFiles}
          />
        </div>
      </PaneBody>
    );
  }
}

export const paneProvider: PaneProvider = {
  getPaneTitle: () => 'Robot Service Task',
  shouldBeDisplayed: shouldBeDisplayed,
  Pane: PaneFull,
  PaneContent: PaneContent,
};
