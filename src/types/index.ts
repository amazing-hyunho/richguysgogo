export type Difficulty='쉬움'|'보통';
export interface Persona{id:string;name:string;age:number;emoji:string;tagline:string;personality:string;difficulty:Difficulty;background:string;interests:string[];speechStyle:string;prompt:string}
export interface Mission{id:string;level:number;title:string;description:string;targetQuestions:number;targetReactions:number;duration:number}
export type Role='elder'|'student'; export interface Message{id:string;role:Role;text:string}
export interface Evaluation{greeting:boolean;question:boolean;reaction:boolean;empathy:boolean;conversationInitiative:boolean;silenceBreak:boolean}
export interface AiResponse{reply:string;evaluation:Evaluation;facts:{key:string;value:string}[]}
export interface GameStats{score:number;greeting:boolean;questions:number;reactions:number;empathy:number;silenceBreaks:number;elapsed:number}
export interface Progress{practiceCount:number;highScore:number;badges:string[];completedPersonas:string[];completedMissions:string[]}
