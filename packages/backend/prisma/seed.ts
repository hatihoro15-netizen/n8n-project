import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('Seeding database...');

  // --- Channels ---
  const lumix = await prisma.channel.upsert({
    where: { slug: 'lumix' },
    update: {},
    create: {
      name: '루믹스 솔루션',
      slug: 'lumix',
      description: '온라인 카지노 통합 솔루션 전문 기업 (pineapplefund.org)',
      isActive: true,
    },
  });

  const onca = await prisma.channel.upsert({
    where: { slug: 'oncasudi' },
    update: {},
    create: {
      name: '온카스터디',
      slug: 'oncasudi',
      description: '먹튀검증 전문 커뮤니티 플랫폼 (maxpixels.net)',
      isActive: true,
    },
  });

  const slot = await prisma.channel.upsert({
    where: { slug: 'slot' },
    update: {},
    create: {
      name: '슬롯',
      slug: 'slot',
      description: '슬롯 게임 정보 채널',
      isActive: true,
    },
  });

  const sports = await prisma.channel.upsert({
    where: { slug: 'sports' },
    update: {},
    create: {
      name: '스포츠',
      slug: 'sports',
      description: '스포츠 숏폼 채널',
      isActive: true,
    },
  });

  console.log('  Channels created:', [lumix.name, onca.name, slot.name, sports.name]);

  // --- Workflows ---
  const workflows = [
    {
      channelId: lumix.id,
      n8nWorkflowId: '9YOHS8N1URWlzGWj',
      name: '루믹스 숏폼 v3',
      type: 'shortform' as const,
      webhookPath: 'lumix-short',
      webhookUrl: 'https://n8n.srv1345711.hstgr.cloud/webhook/lumix-short',
    },
    {
      channelId: lumix.id,
      n8nWorkflowId: 'dsP2aQ1YRyeFRRNA',
      name: '루믹스 롱폼 v1',
      type: 'longform' as const,
      webhookPath: 'lumix-long',
      webhookUrl: 'https://n8n.srv1345711.hstgr.cloud/webhook/lumix-long',
    },
    {
      channelId: onca.id,
      n8nWorkflowId: 'Rn7dlQMowuMGQ72g',
      name: '온카스터디 숏폼 v1',
      type: 'shortform' as const,
      webhookPath: 'onca-short',
      webhookUrl: 'https://n8n.srv1345711.hstgr.cloud/webhook/onca-short',
    },
    {
      channelId: onca.id,
      n8nWorkflowId: 'u8m6S0WheOK6Kvqd',
      name: '온카스터디 롱폼 v1',
      type: 'longform' as const,
      webhookPath: 'onca-long',
      webhookUrl: 'https://n8n.srv1345711.hstgr.cloud/webhook/onca-long',
    },
    {
      channelId: slot.id,
      n8nWorkflowId: 'vhlxnOE44ioOMPtq',
      name: '슬롯 쇼츠 v1',
      type: 'shortform' as const,
      webhookPath: 'slot-short',
      webhookUrl: 'https://n8n.srv1345711.hstgr.cloud/webhook/slot-short',
    },
    {
      channelId: sports.id,
      n8nWorkflowId: 'kJlaa6b2kKj7Jlb9',
      name: '스포츠 숏폼 v1',
      type: 'shortform' as const,
      webhookPath: 'sports-short',
      webhookUrl: 'https://n8n.srv1345711.hstgr.cloud/webhook/sports-short',
    },
    {
      channelId: onca.id,
      n8nWorkflowId: 'jRT8nmDr34S96I1b',
      name: '온카스터디 스토리짤 v7 (할머니+Mike)',
      type: 'story_shorts' as const,
      webhookPath: 'onca-story',
      webhookUrl: 'https://n8n.srv1345711.hstgr.cloud/webhook/onca-story',
    },
  ];

  for (const wf of workflows) {
    await prisma.workflow.upsert({
      where: { id: wf.n8nWorkflowId },
      update: {},
      create: {
        ...wf,
        id: wf.n8nWorkflowId,
        isActive: true,
      },
    });
  }
  console.log('  Workflows created:', workflows.length);

  // --- Characters ---
  const jay = await prisma.character.upsert({
    where: { id: 'char-jay' },
    update: {},
    create: {
      id: 'char-jay',
      name: 'Jay',
      nameKo: '제이',
      personality: '열정적이고 도전적인 청년. 온라인 비즈니스에 관심이 많고 항상 새로운 것을 시도하려는 성격.',
      speechStyle: '캐주얼하고 에너지 넘치는 말투. "야 형, 이거 진짜 대박이야!" 스타일.',
      isActive: true,
    },
  });

  const mike = await prisma.character.upsert({
    where: { id: 'char-mike' },
    update: {},
    create: {
      id: 'char-mike',
      name: 'Mike',
      nameKo: '마이크',
      personality: '신중하고 분석적인 멘토. 업계 경험이 풍부하고 조언을 잘해주는 현실적인 성격.',
      speechStyle: '차분하고 권위 있는 말투. "그래, 근데 이건 좀 더 생각해봐야 해." 스타일.',
      isActive: true,
    },
  });

  const grandma = await prisma.character.upsert({
    where: { id: 'char-grandma' },
    update: {},
    create: {
      id: 'char-grandma',
      name: 'Grandma',
      nameKo: '할머니',
      personality: '인생 경험이 풍부한 할머니. 손자에게 조언해주듯 따뜻하면서도 직설적.',
      speechStyle: '구수한 사투리 섞인 말투. "아이고~ 이놈아, 그런 데 돈 넣으면 쓰나" 스타일.',
      isActive: true,
    },
  });

  console.log('  Characters created:', [jay.name, mike.name, grandma.name]);

  // --- Link characters to story_shorts workflow ---
  const storyWorkflow = workflows.find(w => w.type === 'story_shorts');
  if (storyWorkflow) {
    await prisma.workflowCharacter.upsert({
      where: {
        workflowId_characterId: {
          workflowId: storyWorkflow.n8nWorkflowId,
          characterId: grandma.id,
        },
      },
      update: {},
      create: {
        workflowId: storyWorkflow.n8nWorkflowId,
        characterId: grandma.id,
        role: 'main',
      },
    });
    await prisma.workflowCharacter.upsert({
      where: {
        workflowId_characterId: {
          workflowId: storyWorkflow.n8nWorkflowId,
          characterId: mike.id,
        },
      },
      update: {},
      create: {
        workflowId: storyWorkflow.n8nWorkflowId,
        characterId: mike.id,
        role: 'sub',
      },
    });
    console.log('  Character-Workflow links created for story_shorts');
  }

  console.log('\nSeed complete!');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
