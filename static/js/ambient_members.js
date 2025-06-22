function openLeaveAmbientModal(memberId, ambientId) {
    createConfirmationModal({
        id: 'leaveAmbientModal',
        title: 'Sair do Ambiente',
        message: 'Tem certeza que deseja sair deste ambiente?',
        warningText: 'Esta ação não pode ser desfeita.',
        warningList: [
            'Você perderá acesso a todos os recursos do ambiente',
            'Suas preferências e configurações serão perdidas',
            'Será necessário solicitar nova entrada para retornar'
        ],        confirmText: 'Sair do Ambiente',
        cancelText: 'Cancelar',
        confirmUrl: `/ambient/remove_member/${memberId}/${ambientId}`,
        type: 'danger'
    });
    openConfirmationModal('leaveAmbientModal');
}

function openRemoveMemberModal(memberId, ambientId, memberName) {
    createConfirmationModal({
        id: 'removeMemberModal',
        title: 'Remover Membro',
        message: `Tem certeza que deseja remover ${memberName} deste ambiente?`,
        warningText: 'Esta ação não pode ser desfeita.',
        warningList: [
            'O membro perderá acesso a todos os recursos do ambiente',
            'Todas as preferências e configurações do membro serão perdidas',
            'O membro precisará solicitar nova entrada para retornar'
        ],        confirmText: 'Remover Membro',
        cancelText: 'Cancelar',
        confirmUrl: `/ambient/remove_member/${memberId}/${ambientId}`,
        type: 'warning'
    });
    openConfirmationModal('removeMemberModal');
}