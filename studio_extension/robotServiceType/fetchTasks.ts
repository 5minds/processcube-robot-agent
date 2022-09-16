import { SelectOption, Studio } from '@atlas-engine/atlas_studio_sdk';

export function fetchRobots(url: string, studio: Studio): Promise<Array<RobotTopic>> {
  return studio.http.getJson(`${url}/robot_agents/robots`).then((response) => response.topics as Array<RobotTopic>);
}

export type RobotTopic = {
  name: string;
  topic: string;
};

export type RobotSelectOption = Omit<SelectOption, 'value'> & { value: RobotTopic };
