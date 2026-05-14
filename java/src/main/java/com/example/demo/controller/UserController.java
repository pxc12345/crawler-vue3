package com.example.demo.controller;

import com.example.demo.dto.*;
import com.example.demo.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @PostMapping
    public ApiResponse<UserResponseDTO> create(@Valid @RequestBody UserCreateDTO dto) {
        log.info("创建用户请求: {}", dto.getUsername());
        return ApiResponse.success(userService.create(dto));
    }

    @PutMapping("/{id}")
    public ApiResponse<UserResponseDTO> update(@PathVariable Long id, @Valid @RequestBody UserUpdateDTO dto) {
        log.info("更新用户请求: id={}", id);
        return ApiResponse.success(userService.update(id, dto));
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@PathVariable Long id) {
        log.info("删除用户请求: id={}", id);
        userService.delete(id);
        return ApiResponse.success();
    }

    @GetMapping("/{id}")
    public ApiResponse<UserResponseDTO> getById(@PathVariable Long id) {
        return ApiResponse.success(userService.getById(id));
    }

    @GetMapping("/username/{username}")
    public ApiResponse<UserResponseDTO> getByUsername(@PathVariable String username) {
        return ApiResponse.success(userService.getByUsername(username));
    }

    @GetMapping
    public ApiResponse<PageResponse<UserResponseDTO>> page(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size,
            @RequestParam(required = false) String sortBy,
            @RequestParam(defaultValue = "asc") String sortOrder) {
        PageRequest request = PageRequest.builder()
                .page(page)
                .size(size)
                .sortBy(sortBy)
                .sortOrder(sortOrder)
                .build();
        return ApiResponse.success(userService.page(request));
    }

    @GetMapping("/search")
    public ApiResponse<PageResponse<UserResponseDTO>> search(
            @RequestParam String keyword,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size,
            @RequestParam(required = false) String sortBy,
            @RequestParam(defaultValue = "asc") String sortOrder) {
        PageRequest request = PageRequest.builder()
                .page(page)
                .size(size)
                .sortBy(sortBy)
                .sortOrder(sortOrder)
                .build();
        return ApiResponse.success(userService.search(keyword, request));
    }

    @GetMapping("/status/{status}")
    public ApiResponse<List<UserResponseDTO>> getByStatus(@PathVariable Integer status) {
        return ApiResponse.success(userService.getByStatus(status));
    }

    @GetMapping("/count/{status}")
    public ApiResponse<Long> countByStatus(@PathVariable Integer status) {
        return ApiResponse.success(userService.countByStatus(status));
    }

    @PatchMapping("/{id}/status")
    public ApiResponse<UserResponseDTO> changeStatus(@PathVariable Long id, @RequestParam Integer status) {
        log.info("修改用户状态请求: id={}, status={}", id, status);
        return ApiResponse.success(userService.changeStatus(id, status));
    }

    @DeleteMapping("/batch")
    public ApiResponse<Void> batchDelete(@RequestParam List<Long> ids) {
        log.info("批量删除用户请求: ids={}", ids);
        userService.batchDelete(ids);
        return ApiResponse.success();
    }
}
