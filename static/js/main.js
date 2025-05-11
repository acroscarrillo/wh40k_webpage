$(function(){
  let allDatas = [];
  function initSelect($sel){
    $sel.select2({
      placeholder: 'Search units…',
      data: allDatas.map(d=>({id:d.id, text:`[${d.faction}] ${d.name}`})),
      width: '100%'
    });
  }
  // load once
  $.getJSON('/api/datasheets', d=>{
    allDatas = d;
    initSelect($('#team1-select'));
    initSelect($('#team2-select'));
  });
  $('#setup-form').on('submit', e=>{
    e.preventDefault();
    const payload = {
      team1: $('#team1-select').val()||[],
      team2: $('#team2-select').val()||[],
      team1_name: $('#team1-name').val(),
      team2_name: $('#team2-name').val()
    };
    $.ajax({
      url:'/roster',
      method:'POST',
      contentType:'application/json',
      data: JSON.stringify(payload),
      success: ()=> window.location = '/roster/view'
    });
  });

  // on roster page: delegate delete
  $('body').on('click','.del',function(){
    const team = $(this).data('team');
    const li = $(this).closest('li');
    const id = li.data('id');
    $.ajax({
      url:`/roster/remove?team=${team}`,
      method:'POST',
      contentType:'application/json',
      data: JSON.stringify({id}),
      success: ()=> li.remove()
    });
  });

  // scoreboard page logic
  function recalc(){
    $('#score-table tbody tr').each(function(){
      let sum=0;
      $(this).find('.round').each(function(){
        sum += parseInt(this.value)||0;
      });
      $(this).find('.total').text(sum);
    });
  }
  $('body').on('input','.round', recalc);
  $('#save-scores').click(function(){
    const data = { team1:[], team2:[] };
    $('#score-table tbody tr').each(function(){
      const t = $(this).data('team');
      data[t] = $(this).find('.round').map((_,i)=>parseInt(i.value)||0).get();
    });
    $.ajax({
      url:'/scores',
      method:'POST',
      contentType:'application/json',
      data: JSON.stringify(data),
      success: ()=> alert('Scores saved!')
    });
  });
  recalc();
});
