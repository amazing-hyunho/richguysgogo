import type{Mission}from'../types';export const missions:Mission[]=[
{id:'hello',level:1,title:'먼저 인사하기',description:'밝게 인사하고 이름을 소개해 보세요.',targetQuestions:1,targetReactions:1,duration:60},
{id:'questions',level:2,title:'질문 3개 하기',description:'궁금한 것을 자연스럽게 물어보세요.',targetQuestions:3,targetReactions:1,duration:120},
{id:'silence',level:3,title:'어색한 침묵 깨기',description:'짧은 대답 뒤에 새 화제를 꺼내 보세요.',targetQuestions:3,targetReactions:2,duration:180},
{id:'empathy',level:4,title:'이야기에 공감하기',description:'마음을 알아주는 반응을 해보세요.',targetQuestions:2,targetReactions:3,duration:180},
{id:'master',level:5,title:'자연스럽게 대화하기',description:'3분 동안 편안하게 이야기를 이어가요.',targetQuestions:3,targetReactions:3,duration:180}];
